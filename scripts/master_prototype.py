"""Character Master Prototype: executa uma rota e produz quatro vistas comparáveis.

Uso: python scripts/master_prototype.py a [tentativa]
Saída em artifacts/master_prototype/route_<rota>/<tentativa>/
"""

import sys
import time
from pathlib import Path

from app.core.config import ARTIFACTS_DIR, REPO_ROOT
from app.workers.blender_worker import run_stage
from PIL import Image

BUNDLE = REPO_ROOT / "tools/base_meshes/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
VIEWS = [
    {"name": "frente", "heading": 180, "elevation": 0},
    {"name": "tres_quartos", "heading": 135, "elevation": 0},
    {"name": "perfil", "heading": 90, "elevation": 0},
    {"name": "costas", "heading": 0, "elevation": 0},
]
GAME = [{"name": f"jogo_{v['name']}", "heading": v["heading"], "elevation": 30} for v in VIEWS]
FACE = [
    {"name": "rosto_frente", "heading": 180, "elevation": 0, "focus_z": 1.1, "ortho": .62},
    {"name": "rosto_34", "heading": 135, "elevation": 0, "focus_z": 1.1, "ortho": .62},
]
BACKDROP = (46, 48, 54, 255)


def sheet(folder, names, out):
    images = [Image.open(folder / f"{n}.png").convert("RGBA") for n in names]
    w, h = images[0].size
    canvas = Image.new("RGBA", (w * len(images), h), BACKDROP)
    for index, image in enumerate(images):
        canvas.alpha_composite(image, (index * w, 0))
    canvas.convert("RGB").save(out)


def clay(blend, out, work):
    high = run_stage(
        "master_clay",
        {"width": 900, "height": 1200, "views": VIEWS + GAME + FACE, "output_dir": str(out)},
        work, blend_file=blend, timeout_s=300,
    )
    sheet(out, [v["name"] for v in VIEWS], out / "quatro_vistas.png")
    sheet(out, [v["name"] for v in GAME], out / "quatro_vistas_jogo.png")
    sheet(out, [v["name"] for v in FACE], out / "rosto.png")
    return high.output


def route_a(out):
    blend = out / "master_a.blend"
    started = time.monotonic()
    run = run_stage("master_a", {"blend_path": str(blend)}, out / "work", blend_file=BUNDLE, timeout_s=300)
    print("build", round(time.monotonic() - started, 1), run.output)
    return blend


def route_b(out, glb, yaw):
    """Mesma altura total da Rota A em argila: enquadramento igual, sem favorecer nenhuma."""
    blend = out / "master_b.blend"
    payload = {"glb_path": str(Path(glb).resolve()), "blend_path": str(blend), "target_height_m": 1.5257, "yaw_deg": yaw}
    run = run_stage("master_b", payload, out / "work", timeout_s=300)
    print("import", run.output)
    return blend


def route_c(out, glb, base_attempt, b_chin, b_top):
    """Forma da B sobre a estrutura da A; parte de um .blend aprovado tecnicamente da Rota A."""
    blend = out / "master_c.blend"
    base = ARTIFACTS_DIR / "master_prototype" / "route_a" / base_attempt / "master_a.blend"
    payload = {"glb_path": str(Path(glb).resolve()), "blend_path": str(blend),
               "b_height_m": 1.5257, "yaw_deg": 180.0, "b_chin": b_chin, "b_top": b_top}
    run = run_stage("master_c", payload, out / "work", blend_file=base, timeout_s=560)
    print("rota c", run.output)
    return blend


if __name__ == "__main__":
    route = sys.argv[1]
    attempt = sys.argv[2] if len(sys.argv) > 2 else "t01"
    out = ARTIFACTS_DIR / "master_prototype" / f"route_{route}" / attempt
    out.mkdir(parents=True, exist_ok=True)
    if route == "a":
        blend = route_a(out)
    elif route == "c":
        blend = route_c(out, sys.argv[3], sys.argv[4], float(sys.argv[5]), float(sys.argv[6]))
    else:
        glb = sys.argv[3]
        blend = route_b(out, glb, float(sys.argv[4]) if len(sys.argv) > 4 else 0.0)
    result = clay(blend, out, out / "work")
    print({k: v for k, v in result.items() if k != "views"})
