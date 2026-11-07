"""Medidas e folhas comparativas do Character Master Prototype.

Uso: python scripts/master_metrics.py <a|b> <tentativa> [referencia_rgba.png]
Métricas orientam; aprovação visual é humana (regra 3).
"""

import shutil
import sys
import time

import numpy as np
from app.core.config import ARTIFACTS_DIR, REPO_ROOT, write_json
from app.workers.blender_worker import run_stage
from PIL import Image, ImageDraw

route = sys.argv[1]
attempt = sys.argv[2]
reference = sys.argv[3] if len(sys.argv) > 3 else None
root = ARTIFACTS_DIR / "master_prototype" / f"route_{route}" / attempt
report = {"route": route.upper(), "attempt": attempt}
# Rota B: articulações lidas na vista frontal desta malha (altura total normalizada a 1,5257 m).
B_JOINTS = {
    "pelvis": .64, "waist": .74, "ribs": .84, "neck": 1.03, "chin": 1.08, "top": 1.42,
    "clav": (.05, 1.02), "shoulder": (.18, 1.0), "elbow": (.265, .79), "wrist": (.26, .66),
    "fingers": (.255, .55), "hip": (.09, .64), "knee": (.115, .42), "ankle": (.15, .11),
    "toe": (.165, .2, .02),
}
EXTRA = {"joints": B_JOINTS, "body_exclude": [], "decimate": .2} if route == "b" else {}

POSE = {"upper_arm_l": (-80, 0, 0), "forearm_l": (40, 0, 0), "upper_arm_r": (50, 0, 0),
        "thigh_l": (-55, 0, 0), "shin_l": (70, 0, 0), "thigh_r": (30, 0, 0)}
started = time.monotonic()
posed = root / "posed.blend"
rig = run_stage("master_rigtest", {"pose": POSE, "blend_path": str(posed), **EXTRA}, root / "work",
                blend_file=root / f"master_{route}.blend", timeout_s=420)
report["rig"] = {k: v for k, v in rig.output.items() if k not in ("status", "stage")}
report["rig"]["seconds"] = round(time.monotonic() - started, 1)
run_stage("master_clay", {"width": 900, "height": 1200, "output_dir": str(root / "posed"), "views": [
    {"name": "pose_frente", "heading": 180, "elevation": 0},
    {"name": "pose_34", "heading": 135, "elevation": 0},
    {"name": "pose_perfil", "heading": 90, "elevation": 0},
]}, root / "work", blend_file=posed, timeout_s=180)
images = [Image.open(root / "posed" / f"{n}.png").convert("RGBA") for n in ("pose_frente", "pose_34", "pose_perfil")]
sheet = Image.new("RGBA", (2700, 1200), (46, 48, 54, 255))
for index, image in enumerate(images):
    sheet.alpha_composite(image, (index * 900, 0))
sheet.convert("RGB").save(root / "pose_extrema.png")


def mask_of(path):
    alpha = np.asarray(Image.open(path).convert("RGBA"))[:, :, 3] > 128
    ys, xs = np.nonzero(alpha)
    return alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def resized(mask, size):
    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize(size, Image.LANCZOS)) > 128


def silhouette_iou(mine, theirs):
    h = 800
    a = resized(mine, (round(mine.shape[1] * h / mine.shape[0]), h))
    b = resized(theirs, (round(theirs.shape[1] * h / theirs.shape[0]), h))
    best = 0.0
    width = max(a.shape[1], b.shape[1]) + 120
    for offset in range(0, width - min(a.shape[1], b.shape[1]), 4):
        ca = np.zeros((h, width), bool)
        cb = np.zeros((h, width), bool)
        ca[:, (width - a.shape[1]) // 2:(width - a.shape[1]) // 2 + a.shape[1]] = a
        if offset + b.shape[1] > width:
            break
        cb[:, offset:offset + b.shape[1]] = b
        best = max(best, float((ca & cb).sum() / (ca | cb).sum()))
    return best


if reference:
    theirs = mask_of(reference)
    mine = mask_of(root / "tres_quartos.png")
    report["silhouette_iou_three_quarter"] = round(silhouette_iou(mine, theirs), 3)
    ref = Image.open(reference).convert("RGBA")
    box = ref.getbbox()
    hero = ref.crop(box)
    hero_bg = Image.new("RGBA", hero.size, (46, 48, 54, 255))
    hero_bg.alpha_composite(hero)
    clay = Image.open(root / "tres_quartos.png").convert("RGBA")
    clay_bg = Image.new("RGBA", clay.size, (46, 48, 54, 255))
    clay_bg.alpha_composite(clay)
    clay_rgb = clay_bg.crop(clay.getbbox()).convert("RGB").resize(
        (round(clay.getbbox()[2] - clay.getbbox()[0]) * 1000 // (clay.getbbox()[3] - clay.getbbox()[1]), 1000))
    hero_rgb = hero_bg.convert("RGB").resize((hero.width * 1000 // hero.height, 1000))
    side = Image.new("RGB", (hero_rgb.width + clay_rgb.width + 40, 1000), (46, 48, 54))
    side.paste(hero_rgb, (0, 0))
    side.paste(clay_rgb, (hero_rgb.width + 40, 0))
    ImageDraw.Draw(side).text((10, 8), "referencia (sem equipamentos)", fill=(255, 255, 255))
    side.save(root / "lado_a_lado.png")

for name in ("frente", "tres_quartos", "perfil", "costas"):
    alpha = np.asarray(Image.open(root / f"{name}.png").convert("RGBA"))[:, :, 3]
    report.setdefault("silhouette_area_px", {})[name] = int((alpha > 128).sum())

write_json(root / "metrics.json", report)
evidence = REPO_ROOT / "docs/audit/master_prototype"
evidence.mkdir(parents=True, exist_ok=True)
for name in ("quatro_vistas.png", "quatro_vistas_jogo.png", "rosto.png", "pose_extrema.png", "lado_a_lado.png", "metrics.json"):
    source = root / name
    if source.is_file():
        shutil.copy2(source, evidence / f"rota_{route}_{name}")
print(report)
