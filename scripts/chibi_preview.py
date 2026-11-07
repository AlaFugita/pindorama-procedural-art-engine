"""Monta um personagem chibi e renderiza vistas grandes ao lado do Mago de referência.

Uso: python scripts/chibi_preview.py <spec.json> <saida>
"""

import copy
import sys
from pathlib import Path

from app.core.config import read_json
from app.domain.directions import camera_basis
from app.schemas.contracts import CharacterSpec
from app.workers.blender_worker import run_stage
from engines.character_engine.resolver import Library, resolve
from PIL import Image

spec = CharacterSpec.model_validate(read_json(Path(sys.argv[1])))
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
r = resolve(spec, Library())
blend = out / "character.blend"
run_stage("build", r.build_payload(blend), out, timeout_s=200)
profile = copy.deepcopy(r.render)
scale = 4
profile.canvas.width *= scale
profile.canvas.height *= scale
profile.pixels_per_meter *= scale
profile.pivot.x *= scale
profile.pivot.y *= scale
basis = camera_basis(profile)
payload = {**profile.model_dump(mode="json"), "camera": {"matrix_world": basis.matrix_world(), "ortho_scale": basis.ortho_scale}}
views = {"frente": 180, "lado": 90, "costas": 0, "se": 135}
run_stage("preview", {"render": payload, "headings": views, "output_dir": str(out)}, out, blend_file=blend, timeout_s=200)
sheet = Image.new("RGBA", (512 * 4, 512), (255, 0, 255, 255))
for i, name in enumerate(views):
    sheet.alpha_composite(Image.open(out / f"{name}.png").convert("RGBA"), (i * 512, 0))
sheet.convert("RGB").save(out / "vistas.png")
print("ok")
