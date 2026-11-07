"""Avalia o teste de textura contra a referência, com as métricas da auditoria original.

Uso: python scripts/master_paint_eval.py <tentativa> [prefixo_das_evidencias]
Métricas orientam; a aprovação é humana (regra 3).
"""

import shutil
import sys

import numpy as np
from app.core.config import ARTIFACTS_DIR, REPO_ROOT, write_json
from PIL import Image

BG = (28, 29, 33)
root = ARTIFACTS_DIR / "master_prototype/paint" / sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else "textura"
out = REPO_ROOT / "docs/audit/master_prototype"
reference = Image.open(REPO_ROOT / "docs/audit/evidence/reference.webp").convert("RGB")


def flat(path):
    image = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", image.size, (*BG, 255))
    base.alpha_composite(image)
    return base.crop(image.getbbox()).convert("RGB")


def fit_height(image, height):
    return image.resize((image.width * height // image.height, height), Image.LANCZOS)


def stats(image):
    array = np.asarray(image.convert("RGB"), dtype=float) / 255
    mask = np.abs(array - np.array(BG) / 255).max(axis=2) > .06
    luma = (array * [.2126, .7152, .0722]).sum(axis=2)
    quant = (array[mask] * 31).astype(int)
    gy, gx = np.gradient(luma)
    return {
        "luma_p5": round(float(np.percentile(luma[mask], 5)), 3),
        "luma_p95": round(float(np.percentile(luma[mask], 95)), 3),
        "saturation": round(float((array.max(axis=2) - array.min(axis=2))[mask].mean()), 3),
        "colors_5bit": len(np.unique(quant[:, 0] * 900 + quant[:, 1] * 30 + quant[:, 2])),
        "detail": round(float(np.hypot(gx, gy)[mask].mean()), 4),
    }


hero = reference.crop((0, 0, 430, 1024))
mine = fit_height(flat(root / "tres_quartos.png"), 1024)
sheet = Image.new("RGB", (hero.width + mine.width + 30, 1024), BG)
sheet.paste(hero, (0, 0))
sheet.paste(mine, (hero.width + 30, 0))
sheet.save(root / "lado_a_lado.png")

sprite_ref = reference.crop((868, 10, 985, 185))
sprite = fit_height(flat(root / "jogo_tres_quartos.png"), 175)
zoom = 4
a = sprite_ref.resize((sprite_ref.width * zoom, sprite_ref.height * zoom), Image.NEAREST)
b = sprite.resize((sprite.width * zoom, sprite.height * zoom), Image.NEAREST)
sheet = Image.new("RGB", (a.width + b.width + 30, a.height), BG)
sheet.paste(a, (0, 0))
sheet.paste(b, (a.width + 30, 0))
sheet.save(root / "escala_jogo.png")

report = {"reference_hero": stats(hero), "painted_presentation": stats(mine),
          "reference_sprite": stats(a), "painted_sprite": stats(b)}
write_json(root / "metrics.json", report)
for name in ("quatro_vistas.png", "quatro_vistas_jogo.png", "rosto_34.png", "lado_a_lado.png",
             "escala_jogo.png", "metrics.json"):
    shutil.copy2(root / name, out / f"{prefix}_{name}")
for key, value in report.items():
    print(key, value)
