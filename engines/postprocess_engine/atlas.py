"""Atlas por animação+direção, folhas de contato, previews e QA de imagem (doc 19)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
from app.domain.directions import project_canonical
from app.schemas.contracts import (
    AnimationClip,
    CheckResult,
    ContactEvent,
    DirectionAtlas,
    FrameRect,
    GateStatus,
    Pixel,
    RenderProfile,
)
from PIL import Image, ImageDraw

from engines.postprocess_engine.images import alpha_bbox, check_png, load_rgba

GUTTER_PX = 2
BACKDROP = (58, 74, 66, 255)
LANDMARK_CHECK = ("pelvis", "head", "foot_l", "foot_r", "hand_l", "hand_r")
LANDMARK_RADIUS_PX = 4
IDLE_JITTER_WARN_PX = 4


def _build_trimmed(frames: list[Path], destination: Path, render: RenderProfile) -> DirectionAtlas:
    """Tira horizontal com a caixa justa de cada quadro (+1 px transparente). O quadro cheio é
    reconstruído pela posição (ox, oy): pivô e enquadramento não mudam."""
    width, height = render.canvas.width, render.canvas.height
    crops = []
    for path in frames:
        rgba = load_rgba(path)
        box = alpha_bbox(rgba, threshold=1) or (0, 0, 1, 1)
        x0, y0 = max(0, box[0] - 1), max(0, box[1] - 1)
        x1, y1 = min(width, box[2] + 1), min(height, box[3] + 1)
        crops.append((Image.fromarray(rgba[y0:y1, x0:x1]), x0, y0))
    atlas_width = sum(c[0].width for c in crops) + (len(crops) + 1) * GUTTER_PX
    atlas_height = max(c[0].height for c in crops) + 2 * GUTTER_PX
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    rects, x = [], GUTTER_PX
    for index, (crop, ox, oy) in enumerate(crops):
        atlas.paste(crop, (x, GUTTER_PX))
        rects.append(FrameRect(index=index, x=x, y=GUTTER_PX, w=crop.width, h=crop.height, ox=ox, oy=oy))
        x += crop.width + GUTTER_PX
    destination.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(destination, optimize=True)
    return DirectionAtlas(
        file=destination.name, atlas_width=atlas_width, atlas_height=atlas_height,
        frame_width=width, frame_height=height, frame_count=len(frames), gutter_px=GUTTER_PX,
        heading_deg=render.headings_deg[destination.stem.rsplit("_", 1)[1]],
        pivot=Pixel(x=render.pivot.x, y=render.pivot.y), frames=rects,
    )


def build_atlas(frames: list[Path], destination: Path, render: RenderProfile, heading: float) -> DirectionAtlas:
    """Tira horizontal com canvas fixo; sem redimensionar nem recortar por frame (doc 05 §9).

    Com ``render.atlas_trim``, guarda só a caixa justa de cada quadro (veja ``_build_trimmed``).
    """
    if render.atlas_trim:
        return _build_trimmed(frames, destination, render)
    width, height = render.canvas.width, render.canvas.height
    count = len(frames)
    atlas_width = count * width + (count + 1) * GUTTER_PX
    atlas_height = height + 2 * GUTTER_PX
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    rects = []
    for index, path in enumerate(frames):
        x = GUTTER_PX + index * (width + GUTTER_PX)
        with Image.open(path) as frame:
            atlas.paste(frame.convert("RGBA"), (x, GUTTER_PX))
        rects.append(FrameRect(index=index, x=x, y=GUTTER_PX, w=width, h=height))
    destination.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(destination, optimize=True)
    return DirectionAtlas(
        file=destination.name, atlas_width=atlas_width, atlas_height=atlas_height,
        frame_width=width, frame_height=height, frame_count=count, gutter_px=GUTTER_PX,
        heading_deg=render.headings_deg[destination.stem.rsplit("_", 1)[1]],
        pivot=Pixel(x=render.pivot.x, y=render.pivot.y), frames=rects,
    )


def check_atlas(path: Path, atlas: DirectionAtlas, frame_paths: list[Path]) -> list[str]:
    """IMG-003: retângulos dentro do atlas, sem sobreposição, conteúdo idêntico aos frames."""
    problems: list[str] = []
    rgba = load_rgba(path)
    if rgba.shape[:2] != (atlas.atlas_height, atlas.atlas_width):
        problems.append(f"{path.name}: dimensão {rgba.shape}")
    if len(atlas.frames) != atlas.frame_count or atlas.frame_count != len(frame_paths):
        problems.append(f"{path.name}: contagem de frames incoerente")
    previous_end = 0
    for rect, frame_path in zip(atlas.frames, frame_paths, strict=False):
        if rect.x + rect.w > atlas.atlas_width or rect.y + rect.h > atlas.atlas_height:
            problems.append(f"{path.name}: frame {rect.index} fora do atlas")
            continue
        if rect.x - previous_end < atlas.gutter_px - 0:
            problems.append(f"{path.name}: gutter violado no frame {rect.index}")
        previous_end = rect.x + rect.w
        crop = rgba[rect.y : rect.y + rect.h, rect.x : rect.x + rect.w]
        source = load_rgba(frame_path)
        region = source[rect.oy : rect.oy + rect.h, rect.ox : rect.ox + rect.w]
        outside = source[..., 3].copy()
        outside[rect.oy : rect.oy + rect.h, rect.ox : rect.ox + rect.w] = 0
        if not np.array_equal(crop, region) or outside.any():
            problems.append(f"{path.name}: frame {rect.index} difere da origem")
    return problems


def contact_sheet(images: dict[str, Path], destination: Path, title: str, render: RenderProfile) -> Path:
    """Folha 3×3 com o centro para legenda; posição na grade espelha a bússola (doc 19 §5)."""
    grid = {"NW": (0, 0), "N": (1, 0), "NE": (2, 0), "W": (0, 1), "E": (2, 1),
            "SW": (0, 2), "S": (1, 2), "SE": (2, 2)}
    w, h = render.canvas.width, render.canvas.height
    sheet = Image.new("RGBA", (w * 3, h * 3), BACKDROP)
    draw = ImageDraw.Draw(sheet)
    for name, path in images.items():
        col, row = grid[name]
        with Image.open(path) as image:
            sheet.alpha_composite(image.convert("RGBA"), (col * w, row * h))
        draw.text((col * w + 6, row * h + 6), f"{name}  {render.headings_deg[name]:.0f}°",
                  fill=(255, 255, 255, 255))
    draw.multiline_text((w + 12, h + 12), title, fill=(255, 255, 255, 255), spacing=6)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination)
    return destination


def spritesheet_preview(atlases: dict[str, Path], destination: Path) -> Path:
    images = [Image.open(p).convert("RGBA") for p in atlases.values()]
    width = max(i.width for i in images)
    height = sum(i.height for i in images)
    sheet = Image.new("RGBA", (width, height), BACKDROP)
    y = 0
    for image in images:
        sheet.alpha_composite(image, (0, y))
        y += image.height
    sheet.save(destination)
    return destination


def animated_preview(frames: list[Path], destination: Path, fps: int) -> Path:
    rendered = []
    for path in frames:
        base = Image.new("RGBA", Image.open(path).size, BACKDROP)
        base.alpha_composite(Image.open(path).convert("RGBA"))
        rendered.append(base.convert("P", palette=Image.ADAPTIVE, colors=128))
    rendered[0].save(destination, save_all=True, append_images=rendered[1:], loop=0,
                     duration=round(1000 / fps), disposal=2, optimize=False)
    return destination


def qa_frames(
    clip: AnimationClip,
    render: RenderProfile,
    frames: dict[str, list[Path]],
    trace: list[dict[str, Any]],
) -> tuple[list[CheckResult], dict[str, Any]]:
    """Por clip: IMG-001/002, RND-003 (contagem), DIR-002 (direções distintas), IMG-004."""
    cid = clip.animation_id
    width, height = render.canvas.width, render.canvas.height
    file_problems: list[str] = []
    landmark_problems: list[str] = []
    count_problems: list[str] = []
    jitter: dict[str, tuple[int, int, int, int]] = {}
    digests: dict[str, list[str]] = {}
    for direction in render.direction_order:
        files = frames.get(direction, [])
        if len(files) != clip.frame_count:
            count_problems.append(f"{direction}: {len(files)} frames")
        boxes = []
        digests[direction] = []
        for index, path in enumerate(files):
            problems = check_png(path, width, height, render.safety_margin_px)
            file_problems += problems
            if problems:
                continue
            rgba = load_rgba(path)
            digests[direction].append(hashlib.sha256(rgba.tobytes()).hexdigest())
            boxes.append(alpha_bbox(rgba))
            alpha = rgba[:, :, 3]
            for name in LANDMARK_CHECK:
                x, y = project_canonical(
                    tuple(trace[index]["points"][name]), render.headings_deg[direction], render
                )
                ix, iy = int(x), int(y)
                r = LANDMARK_RADIUS_PX
                region = alpha[max(iy - r, 0) : iy + r + 1, max(ix - r, 0) : ix + r + 1]
                if region.size == 0 or int(region.max()) < 128:
                    landmark_problems.append(f"{direction}/{index}/{name} fora da silhueta")
        if boxes:
            array = np.array(boxes)
            jitter[direction] = tuple(int(v) for v in array.max(axis=0) - array.min(axis=0))

    # Repetição intencional (pose mantida, ``held_frames``) não é duplicação acidental.
    held = set(clip.held_frames)
    repeated = intentional = 0
    for frame_digests in digests.values():
        seen = set()
        for index, digest in enumerate(frame_digests):
            if digest in seen:
                if index in held:
                    intentional += 1
                else:
                    repeated += 1
            seen.add(digest)
    equal_directions = []
    names = list(digests)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            if digests[a] and digests[a] == digests[b]:
                equal_directions.append(f"{a}={b}")

    def status(problems: list[str]) -> GateStatus:
        return GateStatus.FAIL if problems else GateStatus.PASS

    checks = [
        CheckResult(id=f"RND-003:{cid}", status=status(count_problems),
                    detail="; ".join(count_problems) or f"8 direções × {clip.frame_count} frames"),
        CheckResult(id=f"IMG-001:{cid}", status=status(file_problems),
                    detail="; ".join(file_problems[:8]) or "PNG RGBA, dimensões, alpha e sem corte",
                    tolerance=f"margem {render.safety_margin_px}px"),
        CheckResult(id=f"IMG-004:{cid}", status=status(landmark_problems),
                    detail="; ".join(landmark_problems[:8])
                    or "landmarks 3D projetados caem na silhueta em todos os frames",
                    tolerance=f"raio {LANDMARK_RADIUS_PX}px"),
        CheckResult(id=f"DIR-002:{cid}", status=status(equal_directions),
                    detail="; ".join(equal_directions) or "oito direções distintas (sem espelhamento)"),
    ]
    if repeated:
        checks.append(CheckResult(id=f"IMG-005:{cid}", status=GateStatus.WARN,
                                  detail=f"{repeated} frames repetidos dentro de uma direção"))
    if cid == "idle":
        worst = max((max(j) for j in jitter.values()), default=0)
        checks.append(CheckResult(
            id="IMG-002:idle",
            status=GateStatus.WARN if worst > IDLE_JITTER_WARN_PX else GateStatus.PASS,
            detail=f"variação máxima de bbox no idle: {worst}px", tolerance=f"{IDLE_JITTER_WARN_PX}px",
        ))
    return checks, {"bbox_jitter": jitter, "repeated_frames": repeated, "held_repeats": intentional}


def events_of(clip: AnimationClip) -> list[ContactEvent]:
    return sorted(clip.events, key=lambda e: e.frame)
