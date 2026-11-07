"""Evidências da auditoria visual: render em alta resolução e comparações lado a lado.

Uso: python scripts/audit_visual.py <referencia> <saida>
Não altera o pipeline: só sobrepõe a resolução do RenderProfile nesta execução.
"""

import copy
import shutil
import sys
from pathlib import Path

import numpy as np
from app.core.config import PROJECTS_DIR, REPO_ROOT, read_json
from app.domain.directions import camera_basis
from app.schemas.contracts import CharacterSpec
from app.workers.blender_worker import run_stage
from PIL import Image, ImageDraw

from engines.character_engine.resolver import Library, resolve

reference_path, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
reference = Image.open(reference_path).convert("RGB")
print("referência", reference.size)
shutil.copy2(reference_path, out / f"reference{reference_path.suffix}")

spec = CharacterSpec.model_validate(read_json(REPO_ROOT / "tests/fixtures/specs/guardiao_da_floresta.json"))
r = resolve(spec, Library())
blend = next((PROJECTS_DIR / "default/characters/guardiao_da_floresta/stages/animate").glob("*/character.blend"))

SCALE = 5
profile = copy.deepcopy(r.render)
profile.canvas.width *= SCALE
profile.canvas.height *= SCALE
profile.pixels_per_meter *= SCALE
profile.pivot.x *= SCALE
profile.pivot.y *= SCALE
basis = camera_basis(profile)
payload = {**profile.model_dump(mode="json"),
           "camera": {"matrix_world": basis.matrix_world(), "ortho_scale": basis.ortho_scale}}
views = {"frente": 180, "tres_quartos": 135, "perfil": 90, "costas": 0}
run_stage("preview", {"render": payload, "headings": views, "output_dir": str(out)}, out,
          blend_file=blend, timeout_s=180)

BG = (28, 29, 33)


def on_bg(path):
    image = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", image.size, (*BG, 255))
    base.alpha_composite(image)
    return base.convert("RGB")


# 1. Alta resolução: mesmo enquadramento de altura do herói da referência.
hero = reference.crop((0, 0, 430, reference.height))
ours = on_bg(out / "frente.png")
ours = ours.crop(ours.point(lambda v: 255 if v > 40 else 0).getbbox())
ours = ours.resize((round(ours.width * hero.height / ours.height), hero.height), Image.LANCZOS)
sheet = Image.new("RGB", (hero.width + ours.width + 30, hero.height), BG)
sheet.paste(hero, (0, 0))
sheet.paste(ours, (hero.width + 30, 0))
d = ImageDraw.Draw(sheet)
d.text((8, 6), "REFERENCIA", fill=(255, 255, 255))
d.text((hero.width + 38, 6), "ATUAL - 5x resolucao (1280x1600)", fill=(255, 255, 255))
sheet.save(out / "A_alta_resolucao.png")

# 2. Escala de jogo: sprite da referência × nosso frame real, ampliados 3× sem suavizar.
sprite_ref = reference.crop((868, 10, 985, 185))
frame = next((REPO_ROOT / "exports/guardiao_da_floresta/atlases").glob("idle_SE.png"))
atlas = Image.open(frame).convert("RGBA").crop((2, 2, 258, 322))
base = Image.new("RGBA", atlas.size, (*BG, 255))
base.alpha_composite(atlas)
small = base.convert("RGB")
small = small.crop((60, 40, 200, 320))
zoom = 3
a = sprite_ref.resize((sprite_ref.width * zoom, sprite_ref.height * zoom), Image.NEAREST)
factor = a.height / small.height
b = small.resize((round(small.width * factor), a.height), Image.NEAREST)
sheet = Image.new("RGB", (a.width + b.width + 30, a.height), BG)
sheet.paste(a, (0, 0))
sheet.paste(b, (a.width + 30, 0))
sheet.save(out / "B_escala_de_jogo.png")


# 3. Medidas objetivas de valor e cor.
def stats(image, label):
    array = np.asarray(image.convert("RGB"), dtype=float) / 255
    mask = (np.abs(array - np.array(BG) / 255).max(axis=2) > .06)
    luma = (array * [.2126, .7152, .0722]).sum(axis=2)[mask]
    sat = (array.max(axis=2) - array.min(axis=2))[mask]
    quant = (array[mask] * 31).astype(int)
    colours = len(np.unique(quant[:, 0] * 900 + quant[:, 1] * 30 + quant[:, 2]))
    gy, gx = np.gradient((array * [.2126, .7152, .0722]).sum(axis=2))
    edges = float(np.hypot(gx, gy)[mask].mean())
    print(f"{label}: luma p5/p95 {np.percentile(luma, 5):.2f}/{np.percentile(luma, 95):.2f} "
          f"sat méd {sat.mean():.2f} cores(5bit) {colours} detalhe {edges:.4f} pixels {int(mask.sum())}")


stats(hero, "referência herói")
stats(ours, "atual 5x")
stats(a, "referência sprite")
stats(b, "atual sprite")
