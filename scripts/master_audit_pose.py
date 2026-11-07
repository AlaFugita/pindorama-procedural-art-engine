"""Roda a sonda de chão e túnica sobre o .blend animado mais recente de um personagem.

Uso: python scripts/master_audit_pose.py <slug> <saida.json>
"""

import json
import sys
from pathlib import Path

from app.workers.blender_worker import run_stage

slug, out = sys.argv[1], Path(sys.argv[2]).resolve()
root = (Path("projects/default/characters") / slug / "stages/animate").resolve()
folder = max(root.iterdir(), key=lambda p: p.stat().st_mtime)
blend = folder / "character.blend"
work = out.parent / f"_probe_{slug}"
work.mkdir(parents=True, exist_ok=True)
result = run_stage("audit_pose", {}, work, blend_file=blend, timeout_s=600).output
result["blend"] = str(blend)
out.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
for clip, data in result["clips"].items():
    low = list(data["min_z"].items())[:4]
    print(clip, "abaixo do chão:", low, "coxa fora (vértices, mm):", [(f["vertices"], f["max_mm"]) for f in data["thigh_out_per_frame"]])
