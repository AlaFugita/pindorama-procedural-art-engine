"""Verificações determinísticas de imagem (doc 19 §3)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def load_rgba(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"{path.name}: formato {image.format}, esperado PNG")
        if image.mode != "RGBA":
            raise ValueError(f"{path.name}: modo {image.mode}, esperado RGBA")
        image.load()
        return np.asarray(image, dtype=np.uint8).copy()


def alpha_bbox(rgba: np.ndarray, threshold: int = 8) -> tuple[int, int, int, int] | None:
    """(x0, y0, x1, y1) exclusivo em x1/y1, ou None se não houver pixels visíveis."""
    mask = rgba[:, :, 3] >= threshold
    if not mask.any():
        return None
    ys = np.flatnonzero(mask.any(axis=1))
    xs = np.flatnonzero(mask.any(axis=0))
    return int(xs[0]), int(ys[0]), int(xs[-1]) + 1, int(ys[-1]) + 1


def check_png(
    path: Path, width: int, height: int, margin: int = 0, min_visible_px: int = 16
) -> list[str]:
    """Lista de violações objetivas; vazia significa aprovado."""
    problems: list[str] = []
    if not path.is_file() or path.stat().st_size == 0:
        return [f"{path.name}: ausente ou vazio"]
    if path.read_bytes()[:8] != PNG_SIGNATURE:
        return [f"{path.name}: assinatura PNG inválida"]
    try:
        rgba = load_rgba(path)
    except (ValueError, OSError) as error:
        return [f"{path.name}: {error}"]
    if rgba.shape[:2] != (height, width):
        problems.append(f"{path.name}: dimensões {rgba.shape[1]}x{rgba.shape[0]}")
    alpha = rgba[:, :, 3]
    visible = int((alpha >= 8).sum())
    if visible < min_visible_px:
        problems.append(f"{path.name}: sem pixels visíveis ({visible})")
        return problems
    corners = [alpha[0, 0], alpha[0, -1], alpha[-1, 0], alpha[-1, -1]]
    if any(int(c) != 0 for c in corners):
        problems.append(f"{path.name}: fundo opaco nos cantos")
    if float((alpha == 0).mean()) < 0.05:
        problems.append(f"{path.name}: quase sem transparência")
    box = alpha_bbox(rgba)
    if box is not None:
        x0, y0, x1, y1 = box
        h, w = rgba.shape[:2]
        if x0 < margin or y0 < margin or x1 > w - margin or y1 > h - margin:
            problems.append(f"{path.name}: silhueta {box} invade a margem de {margin}px (corte)")
    return problems


def color_centroid(
    rgba: np.ndarray, target: tuple[int, int, int], tolerance: int = 60, min_alpha: int = 128
) -> tuple[float, float, int] | None:
    """Centroide (x, y em pixel contínuo) e área dos pixels próximos de ``target``."""
    mask = rgba[:, :, 3] >= min_alpha
    delta = np.abs(rgba[:, :, :3].astype(int) - np.array(target, dtype=int)).max(axis=2)
    mask &= delta <= tolerance
    count = int(mask.sum())
    if count == 0:
        return None
    ys, xs = np.nonzero(mask)
    return float(xs.mean()) + 0.5, float(ys.mean()) + 0.5, count
