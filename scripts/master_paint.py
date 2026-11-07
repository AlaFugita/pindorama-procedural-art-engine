"""Teste de direção de textura sobre a base aprovada (Rota C t09). Só local.

Uso: python scripts/master_paint.py <tentativa> [corpo]
"""

import sys

from app.core.config import ARTIFACTS_DIR, LIBRARY_DIR, REPO_ROOT, read_json
from app.workers.blender_worker import run_stage
from PIL import Image

base = REPO_ROOT / "library/masters/guardiao_t09/master_c.blend"
root = ARTIFACTS_DIR / "master_prototype/paint" / sys.argv[1]
root.mkdir(parents=True, exist_ok=True)
blend = root / "master_paint.blend"
payload = {
    "glb_path": str((ARTIFACTS_DIR / "master_prototype/route_b/raw/seed42_v4_hier.glb").resolve()),
    "reference_rgba": str((ARTIFACTS_DIR / "master_prototype/route_b/input/hero_rgba_v2.png").resolve()),
    "blend_path": str(blend), "b_height_m": 1.5257, "yaw_deg": 180.0, "b_chin": 1.085,
    "ref_chin_row": 345,
    "art": read_json(LIBRARY_DIR / "profiles/art/pindorama_stylized_v1.json"),
}
if len(sys.argv) > 2 and sys.argv[2] == "corpo":
    payload.update(body_paint=True, sun_energy=1.25)
run = run_stage("master_paint", payload, root / "work", blend_file=base, timeout_s=560)
print({k: v for k, v in run.output.items() if k not in ("status", "stage")})
VIEWS = [{"name": n, "heading": h, "elevation": 0} for n, h in
         (("frente", 180), ("tres_quartos", 135), ("perfil", 90), ("costas", 0))]
GAME = [{"name": f"jogo_{v['name']}", "heading": v["heading"], "elevation": 30} for v in VIEWS]
FACE = [{"name": "rosto_34", "heading": 135, "elevation": 0, "focus_z": 1.1, "ortho": .62}]
run_stage("master_clay", {"width": 900, "height": 1200, "views": VIEWS + GAME + FACE, "output_dir": str(root),
                          "painted": True, "ortho": 1.72}, root / "work", blend_file=blend, timeout_s=400)


def sheet(names, target):
    images = [Image.open(root / f"{n}.png").convert("RGBA") for n in names]
    w, h = images[0].size
    canvas = Image.new("RGBA", (w * len(images), h), (28, 29, 33, 255))
    for index, image in enumerate(images):
        canvas.alpha_composite(image, (index * w, 0))
    canvas.convert("RGB").save(root / target)


sheet([v["name"] for v in VIEWS], "quatro_vistas.png")
sheet([v["name"] for v in GAME], "quatro_vistas_jogo.png")
print("ok")
