"""Composição de pixel art a partir dos passes nativos (id, luz, profundidade).

Não é redução de resolução: cada pixel já nasce na grade final. Aqui se decide, por regra:
1. o papel do material de cada pixel (pela peça);
2. o tom na rampa do material (luz direcional × oclusão), com matiz girando nas sombras;
3. brilho especular só em materiais que o têm; padrão de tecido/madeira como degrau de tom;
4. linhas internas onde a profundidade salta; contorno externo seletivo (sel-out);
5. limpeza de ilhas de pixel menores que o mínimo, exceto materiais protegidos;
6. alpha binário: nenhum pixel semitransparente, nenhum halo.
"""

from __future__ import annotations

import colorsys
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from app.schemas.contracts import PixelArtSettings, PixelMaterialRole


def hex_rgb(value: str) -> np.ndarray:
    value = value.lstrip("#")
    return np.array([int(value[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _shift(rgb: np.ndarray, value: float, hue_deg: float, sat: float = 1.0) -> np.ndarray:
    h, s, v = colorsys.rgb_to_hsv(*(rgb / 255.0))
    h = (h + hue_deg / 360.0) % 1.0
    out = colorsys.hsv_to_rgb(h, min(1.0, s * sat), min(1.0, v * value))
    return np.round(np.array(out) * 255.0)


def ramp(base: np.ndarray, role: PixelMaterialRole) -> np.ndarray:
    """Tons do escuro ao claro. Sombras giram rumo ao frio e ganham saturação; o claro esquenta."""
    lo, hi = role.value_range
    tones = []
    for k in range(role.tones):
        t = k / max(1, role.tones - 1)
        value = lo + (hi - lo) * t
        hue = role.shadow_hue_shift_deg * (1 - t) - role.shadow_hue_shift_deg * .25 * t
        tones.append(_shift(base, value, hue, sat=1.0 + .18 * (1 - t)))
    return np.array(tones)


def role_of(name: str, part_roles: dict[str, str]) -> str:
    if name in part_roles:
        return part_roles[name]
    best = max((p for p in part_roles if p != "*" and name.startswith(p)), key=len, default=None)
    return part_roles[best] if best else part_roles.get("*", "default")


@dataclass
class Passes:
    ids: np.ndarray      # int, 0 = vazio
    light: np.ndarray    # 0..1 (luz/2)
    ao: np.ndarray       # 0..1
    pattern: np.ndarray  # bool
    depth: np.ndarray    # metros


def load_passes(folder: Path, frame: int, depth_range: tuple[float, float]) -> Passes:
    def read(kind):
        return np.asarray(Image.open(folder / f"{frame:04d}_{kind}.png"))

    ident = read("id")
    alpha = ident[..., 3] > (ident.max() / 2 if ident.dtype == np.uint16 else 127)
    scale = 65535.0 if ident.dtype == np.uint16 else 255.0
    ids = np.where(alpha, np.round(ident[..., 0] / scale * 255.0).astype(int), 0)
    light = read("light").astype(np.float64) / (65535.0 if read("light").dtype == np.uint16 else 255.0)
    depth_raw = read("depth").astype(np.float64)
    depth_raw = depth_raw[..., 0] / (65535.0 if depth_raw.max() > 255 else 255.0)
    near, far = depth_range
    return Passes(ids=ids, light=light[..., 0], ao=light[..., 1], pattern=light[..., 2] > .5,
                  depth=near + depth_raw * (far - near))


def compose(p: Passes, parts: list[dict], cfg: PixelArtSettings) -> Image.Image:
    h, w = p.ids.shape
    rgb = np.zeros((h, w, 3))
    tone_index = np.full((h, w), -1)
    role_map = np.full((h, w), "", dtype=object)
    ramps, outlines, roles = {}, {}, {}
    for part in parts:
        mask = p.ids == part["index"]
        if not mask.any():
            continue
        role_name = role_of(part["name"], cfg.part_roles)
        role = cfg.roles[role_name]
        base = hex_rgb(role.base or part.get("color") or "#888888")
        key = (role_name, tuple(base))
        if key not in ramps:
            ramps[key] = ramp(base, role)
            dark = ramps[key][0]
            outlines[key] = hex_rgb(role.outline) if role.outline else dark
        roles[part["index"]] = (key, role)
    # 1-3. tom por pixel
    bands = np.array(cfg.light_bands)
    for index, (key, role) in roles.items():
        mask = p.ids == index
        tones = ramps[key]
        if not role.shading:
            rgb[mask] = tones[-1]
            tone_index[mask] = len(tones) - 1
            role_map[mask] = key[0]
            continue
        lit = p.light[mask] * 2.0
        lit = lit * (1 - role.ao_strength * (1 - p.ao[mask]))
        level = np.searchsorted(bands, lit)
        level = np.clip(np.round(level * (len(tones) - 1) / max(1, len(bands))).astype(int), 0, len(tones) - 1)
        if role.pattern:
            level = np.where(p.pattern[mask], np.maximum(level - 1, 0), level)
        if role.emissive:
            level = np.full_like(level, len(tones) - 1)
        colors = tones[level]
        if role.highlight:
            shine = lit >= role.highlight_threshold * 2.0 * bands[-1] / max(bands[-1], 1e-6)
            colors[shine] = hex_rgb(role.highlight)
        rgb[mask] = colors
        tone_index[mask] = level
        role_map[mask] = key[0]
    solid = p.ids > 0
    # 5. ilhas pequenas → tom vizinho mais comum (por material, exceto protegidos)
    protected = np.zeros_like(solid)
    for index, (_, role) in roles.items():
        if role.protect:
            protected |= p.ids == index
    if cfg.cluster_min_px > 1:
        key_img = (p.ids * 16 + np.maximum(tone_index, 0))
        for value in np.unique(key_img[solid & ~protected]):
            labels, count = ndimage.label(key_img == value)
            if count == 0:
                continue
            sizes = ndimage.sum(np.ones_like(labels), labels, range(1, count + 1))
            for label, size in enumerate(sizes, start=1):
                if size >= cfg.cluster_min_px:
                    continue
                ys, xs = np.nonzero(labels == label)
                for y, x in zip(ys, xs):
                    y0, y1, x0, x1 = max(0, y - 1), min(h, y + 2), max(0, x - 1), min(w, x + 2)
                    win = key_img[y0:y1, x0:x1]
                    same_part = (p.ids[y0:y1, x0:x1] == p.ids[y, x]) & (win != value)
                    if same_part.any():
                        vals, counts = np.unique(win[same_part], return_counts=True)
                        best = vals[np.argmax(counts)]
                        src = np.argwhere(win == best)[0]
                        rgb[y, x] = rgb[y0 + src[0], x0 + src[1]]
    # 4a. linhas internas: o pixel mais distante, junto a um salto de profundidade, escurece
    # Entre peças diferentes basta o salto do perfil; dentro da mesma peça (dobras do capuz,
    # barra da túnica) só um salto grande vira linha, senão a dobra ganha contorno de recorte.
    line = np.zeros_like(solid)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        neighbour_depth = np.roll(p.depth, (dy, dx), axis=(0, 1))
        neighbour_solid = np.roll(solid, (dy, dx), axis=(0, 1))
        same = np.roll(p.ids, (dy, dx), axis=(0, 1)) == p.ids
        jump = p.depth - neighbour_depth
        limit = np.where(same, cfg.internal_line_depth_m * 2.6, cfg.internal_line_depth_m)
        line |= solid & neighbour_solid & (jump > limit)
    ink = hex_rgb(cfg.outline_ink)
    for index, (key, role) in roles.items():
        if role.protect:
            continue
        mask = line & (p.ids == index)
        rgb[mask] = outlines[key] * (1 - cfg.outline_ink_mix * .6) + ink * cfg.outline_ink_mix * .6
    # 4b. contorno externo seletivo
    alpha = solid.copy()
    if cfg.outline_mode == "outside":
        ring = ndimage.binary_dilation(solid, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])) & ~solid
        target = ring
    else:
        target = solid & ~ndimage.binary_erosion(solid)
    ys, xs = np.nonzero(target)
    for y, x in zip(ys, xs):
        y0, y1, x0, x1 = max(0, y - 1), min(h, y + 2), max(0, x - 1), min(w, x + 2)
        neigh = p.ids[y0:y1, x0:x1]
        inside = neigh[neigh > 0]
        if cfg.outline_mode == "inside":
            inside = np.array([p.ids[y, x]])
        if len(inside) == 0:
            continue
        index = np.bincount(inside).argmax()
        key, role = roles[index]
        lit = tone_index[y0:y1, x0:x1][neigh == index].max(initial=0) >= len(ramps[key]) - 1
        mix = cfg.lit_outline_mix if lit else cfg.outline_ink_mix
        rgb[y, x] = outlines[key] * (1 - mix) + ink * mix
        alpha[y, x] = True
    # efeito luminoso: anel de brilho em volta de materiais emissivos
    for index, (key, role) in roles.items():
        if not role.emissive or cfg.glow_radius_px <= 0:
            continue
        core = p.ids == index
        halo = ndimage.binary_dilation(core, iterations=cfg.glow_radius_px) & ~core
        glow = ramps[key][-1] * .6 + 255 * .4
        rgb[halo] = rgb[halo] * .35 + glow * .65
        alpha |= halo
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., :3] = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    out[..., 3] = np.where(alpha, 255, 0)
    out[~alpha, :3] = 0
    return Image.fromarray(out, "RGBA")


def compose_folder(passes_root: Path, frames_root: Path, cfg: PixelArtSettings,
                   clips: list[dict], directions: list[str], depth_range: tuple[float, float]) -> dict:
    parts = json.loads((passes_root / "parts.json").read_text(encoding="utf-8"))
    index: dict[str, dict[str, list[str]]] = {}
    for clip in clips:
        name = clip["animation_id"]
        index[name] = {}
        for direction in directions:
            src = passes_root / name / direction
            dst = frames_root / name / direction
            dst.mkdir(parents=True, exist_ok=True)
            files = []
            for frame in range(clip["frame_count"]):
                image = compose(load_passes(src, frame, depth_range), parts, cfg)
                path = dst / f"{name}_{direction}_{frame:04d}.png"
                image.save(path, optimize=True)
                files.append(str(path))
            index[name][direction] = files
    return index
