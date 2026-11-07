"""Sonda de risco autorizada pelo usuário: um sprite pintado ao lado do sprite da referência.

Uso: python scripts/master_paint_test.py <tentativa_c> <referencia> [rodada]
"""

import copy
import sys

import numpy as np
from app.core.config import ARTIFACTS_DIR, LIBRARY_DIR, REPO_ROOT, read_json
from app.domain.directions import camera_basis
from app.schemas.contracts import RenderProfile
from app.workers.blender_worker import run_stage
from PIL import Image

attempt, reference = sys.argv[1], sys.argv[2]
label = sys.argv[3] if len(sys.argv) > 3 else "p01"
root = ARTIFACTS_DIR / "master_prototype" / "route_c" / attempt
out = root / "paint" / label
out.mkdir(parents=True, exist_ok=True)
BG = (28, 29, 33, 255)

base = RenderProfile.model_validate(read_json(LIBRARY_DIR / "profiles/render/isometric_8dir_v1.json"))
art = read_json(LIBRARY_DIR / "profiles/art/pindorama_stylized_v1.json")
art["toon_steps"] = [[0.0, .42], [.3, .72], [.58, 1.0]]
art["outline_thickness_m"] = .006
art["lights"][0]["energy"] = 1.55
art["lights"][1]["energy"] = .35
art["world_strength"] = .16


def shot(name, heading, scale):
    profile = copy.deepcopy(base)
    profile.canvas.width *= scale
    profile.canvas.height *= scale
    profile.pixels_per_meter *= scale
    profile.pivot.x *= scale
    profile.pivot.y *= scale
    basis = camera_basis(profile)
    render = {**profile.model_dump(mode="json"),
              "camera": {"matrix_world": basis.matrix_world(), "ortho_scale": basis.ortho_scale}}
    return {"name": name, "heading": heading, "render": render}


shots = [shot("sprite_se", 135, 1), shot("sprite_s", 180, 1), shot("apresentacao_se", 135, 4)]
run_stage("master_probe", {"art": art, "shots": shots, "output_dir": str(out)}, out / "work",
          blend_file=root / "master_c.blend", timeout_s=300)

prancha = Image.open(reference).convert("RGB")
ref = prancha.crop((868, 10, 985, 170))


def flat(path):
    image = Image.open(path).convert("RGBA")
    box = image.getbbox()
    back = Image.new("RGBA", image.size, BG)
    back.alpha_composite(image)
    return back.crop(box).convert("RGB")


mine = flat(out / "sprite_se.png")
zoom = 4
height = ref.height * zoom
left = ref.resize((ref.width * zoom, height), Image.NEAREST)
right = mine.resize((mine.width * ref.height // mine.height, ref.height), Image.LANCZOS)
right = right.resize((right.width * zoom, height), Image.NEAREST)
sheet = Image.new("RGB", (left.width + right.width + 60, height), BG[:3])
sheet.paste(left, (0, 0))
sheet.paste(right, (left.width + 60, 0))
sheet.save(out / "teste_sprite.png")

hero = flat(out / "apresentacao_se.png")
hero = hero.resize((hero.width * 1000 // hero.height, 1000), Image.LANCZOS)
ref_hero = prancha.crop((0, 0, 430, 1024)).resize((420, 1000), Image.LANCZOS)
sheet = Image.new("RGB", (ref_hero.width + hero.width + 40, 1000), BG[:3])
sheet.paste(ref_hero, (0, 0))
sheet.paste(hero, (ref_hero.width + 40, 0))
sheet.save(out / "teste_apresentacao.png")


def measure(image):
    array = np.asarray(image, dtype=float) / 255
    mask = np.abs(array - np.array(BG[:3]) / 255).max(axis=2) > .06
    luma = (array * [.2126, .7152, .0722]).sum(axis=2)
    gy, gx = np.gradient(luma)
    quant = (array[mask] * 31).astype(int)
    return {"sombra_p5": round(float(np.percentile(luma[mask], 5)), 3),
            "luz_p95": round(float(np.percentile(luma[mask], 95)), 3),
            "detalhe": round(float(np.hypot(gx, gy)[mask].mean()), 4),
            "cores": len(np.unique(quant[:, 0] * 900 + quant[:, 1] * 30 + quant[:, 2]))}


print("referencia", measure(ref))
print("mestre", measure(mine.resize((mine.width * ref.height // mine.height, ref.height), Image.LANCZOS)))
print(REPO_ROOT.name, out.name)
