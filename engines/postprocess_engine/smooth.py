"""Composição de ilustração suave a partir dos passes nativos (id, luz, profundidade).

Mesmos passes do pixel art, outra regra de composição:
1. passes renderizados em N× a resolução final (supersample);
2. tom contínuo por material: transições suaves (smoothstep) entre tons com giro de matiz;
3. oclusão suave; padrão do material como leve escurecimento (textura discreta);
4. highlight com borda suave só em materiais com brilho; emissivos com brilho difuso;
5. contorno externo com espessura variável (mais grosso no lado da sombra), na cor da peça
   escurecida; linhas internas finas onde a profundidade salta;
6. redução por média com alpha pré-multiplicado: antialiasing real, sem halo de fundo.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from app.schemas.contracts import SmoothArtSettings
from engines.postprocess_engine.pixel import Passes, hex_rgb, load_passes, ramp, role_of


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(e1 - e0, 1e-6), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _tone_position(s: np.ndarray, bands: list[float], soft: float) -> np.ndarray:
    """Posição contínua 0..len(bands) na rampa: degraus suaves em vez de cortes secos."""
    pos = np.zeros_like(s)
    for b in bands:
        pos += _smoothstep(b - soft, b + soft, s)
    return pos


def _sample_ramp(tones: np.ndarray, pos: np.ndarray, bands: int) -> np.ndarray:
    x = pos * (len(tones) - 1) / max(1, bands)
    lo = np.clip(np.floor(x).astype(int), 0, len(tones) - 1)
    hi = np.clip(lo + 1, 0, len(tones) - 1)
    f = (x - lo)[..., None]
    return tones[lo] * (1 - f) + tones[hi] * f


def _disk(radius: float) -> np.ndarray:
    r = max(1, int(np.ceil(radius)))
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= radius * radius


def compose_smooth(p: Passes, parts: list[dict], cfg: SmoothArtSettings) -> Image.Image:
    ss = cfg.supersample
    h, w = p.ids.shape
    rgb = np.zeros((h, w, 3))
    solid = p.ids > 0
    darkest = np.zeros((h, w, 3))
    emissive = np.zeros((h, w), bool)
    glow_color = np.zeros((h, w, 3))
    for part in parts:
        mask = p.ids == part["index"]
        if not mask.any():
            continue
        role = cfg.roles[role_of(part["name"], cfg.part_roles)]
        base = hex_rgb(role.base or part.get("color") or "#888888")
        tones = ramp(base, role)
        outline = hex_rgb(role.outline) if role.outline else tones[0]
        darkest[mask] = outline
        if not role.shading:
            rgb[mask] = tones[-1]
            continue
        s = p.light[mask] * 2.0 * (1 - role.ao_strength * (1 - p.ao[mask]))
        if role.emissive:
            rgb[mask] = tones[-1]
            emissive |= mask
            glow_color[mask] = tones[-1]
        else:
            pos = _tone_position(s, cfg.light_bands, cfg.band_softness)
            if role.pattern:
                pos = pos - p.pattern[mask] * cfg.texture_strength
            if p.noise is not None and cfg.noise_strength > 0:
                pos = pos + (p.noise[mask] - .5) * 2 * cfg.noise_strength
            colors = _sample_ramp(tones, np.clip(pos, 0, len(cfg.light_bands)), len(cfg.light_bands))
            if role.highlight:
                k = _smoothstep(role.highlight_threshold - cfg.band_softness, role.highlight_threshold + cfg.band_softness, s)
                colors = colors * (1 - k[:, None]) + hex_rgb(role.highlight) * k[:, None]
            rgb[mask] = colors
    # Luz de borda: faixa junto à silhueta, só onde a normal de tela aponta para a luz.
    if cfg.rim_px > 0 and cfg.rim_strength > 0:
        inside = ndimage.distance_transform_edt(solid)
        soft = ndimage.gaussian_filter(solid.astype(np.float64), ss * 1.5)
        gy, gx = np.gradient(soft)
        length = np.maximum(np.hypot(gx, gy), 1e-6)
        lx, ly = -cfg.shadow_side[0], -cfg.shadow_side[1]  # luz vem do lado oposto à sombra
        facing = np.clip((-gx * lx - gy * ly) / length, 0, 1)
        band = 1 - _smoothstep(0, cfg.rim_px * ss, inside)
        k = (band * facing * cfg.rim_strength * solid)[..., None]
        rgb = rgb * (1 - k) + hex_rgb(cfg.rim_color) * k
    ink = hex_rgb(cfg.outline_ink)
    # Linhas internas: pixel do lado mais distante de um salto de profundidade, engrossado.
    line = np.zeros_like(solid)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        same = np.roll(p.ids, (dy, dx), axis=(0, 1)) == p.ids
        jump = p.depth - np.roll(p.depth, (dy, dx), axis=(0, 1))
        limit = np.where(same, cfg.internal_line_depth_m * 2.6, cfg.internal_line_depth_m)
        line |= solid & np.roll(solid, (dy, dx), axis=(0, 1)) & (jump > limit)
    if cfg.internal_line_px > 0 and line.any():
        line = ndimage.binary_dilation(line, structure=_disk(cfg.internal_line_px * ss / 2)) & solid
        k = cfg.internal_line_strength
        rgb[line] = rgb[line] * (1 - k) + (darkest[line] * (1 - cfg.outline_ink_mix) + ink * cfg.outline_ink_mix) * k
    # Contorno externo: espessura base + peso extra deslocado para o lado da sombra.
    alpha = solid.astype(np.float64)
    if cfg.outline_px > 0:
        base = ndimage.binary_dilation(solid, structure=_disk(cfg.outline_px * ss))
        sx, sy = cfg.shadow_side
        off = (int(round(sy * cfg.outline_shadow_extra_px * ss)), int(round(sx * cfg.outline_shadow_extra_px * ss)))
        heavy = np.roll(ndimage.binary_dilation(solid, structure=_disk(cfg.outline_px * ss * .8)), off, axis=(0, 1))
        ring = (base | heavy) & ~solid
        _, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
        near = darkest[iy, ix]
        rgb[ring] = near[ring] * (1 - cfg.outline_ink_mix) + ink * cfg.outline_ink_mix
        alpha[ring] = 1.0
    # Brilho difuso dos emissivos (soma de luz, também fora da silhueta).
    if emissive.any() and cfg.glow_radius_px > 0:
        sigma = cfg.glow_radius_px * ss / 2
        weight = ndimage.gaussian_filter(emissive.astype(np.float64), sigma)
        weight = np.clip(weight / max(weight.max(), 1e-6), 0, 1) * cfg.glow_strength
        colour = np.stack([ndimage.gaussian_filter(glow_color[..., c], sigma) for c in range(3)], -1)
        colour /= np.maximum(ndimage.gaussian_filter(emissive.astype(np.float64), sigma)[..., None], 1e-6)
        colour = np.clip(colour * .5 + 255 * .5, 0, 255)
        lit = weight[..., None]
        inside = alpha >= 1
        rgb[inside] = rgb[inside] * (1 - lit[inside]) + colour[inside] * lit[inside]
        halo = ~inside & (weight > .02)
        rgb[halo] = colour[halo]
        alpha = np.maximum(alpha, np.where(halo, weight, 0))
    # Redução com alpha pré-multiplicado (média de blocos ss×ss).
    h2, w2 = h // ss, w // ss
    pre = rgb * alpha[..., None]
    pre = pre[:h2 * ss, :w2 * ss].reshape(h2, ss, w2, ss, 3).mean(axis=(1, 3))
    a = alpha[:h2 * ss, :w2 * ss].reshape(h2, ss, w2, ss).mean(axis=(1, 3))
    out = np.zeros((h2, w2, 4), dtype=np.uint8)
    safe = np.maximum(a, 1e-6)[..., None]
    out[..., :3] = np.clip(np.round(pre / safe), 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return Image.fromarray(out, "RGBA")


def compose_folder(passes_root: Path, frames_root: Path, cfg: SmoothArtSettings,
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
                image = compose_smooth(load_passes(src, frame, depth_range), parts, cfg)
                path = dst / f"{name}_{direction}_{frame:04d}.png"
                image.save(path, optimize=True)
                files.append(str(path))
            index[name][direction] = files
    return index
