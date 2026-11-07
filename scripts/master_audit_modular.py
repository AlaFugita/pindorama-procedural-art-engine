"""Prova de personalização modular: compara cada variação com o Aprendiz base.

Lê o ``build.output.json`` mais recente de cada personagem (hash da malha de cada peça) e o
``character.json`` exportado. Mostra que só as peças do componente trocado mudaram e que rig,
animação e perfil de render são os mesmos. Gera também a folha visual lado a lado.

Uso: python scripts/master_audit_modular.py <saida>
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
CHARS = Path("projects/default/characters")
BASE = "aprendiz"
VARIANTS = ["aprendiz_var_capuz", "aprendiz_var_cabelo", "aprendiz_var_roupa", "aprendiz_var_acessorio", "aprendiz_var_arma"]


def latest(slug, stage):
    return max((CHARS / slug / "stages" / stage).iterdir(), key=lambda p: p.stat().st_mtime)


def build(slug):
    data = json.loads((latest(slug, "build") / "build.output.json").read_text(encoding="utf-8"))
    return {o["name"]: o for o in data["objects"]}


def spec(slug):
    return json.loads((Path("exports") / slug / "character.json").read_text(encoding="utf-8"))


def diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diff(a.get(k), b.get(k), f"{path}.{k}" if path else k)
        return out
    return [] if a == b else [f"{path}: {a!r} → {b!r}"]


base_parts, base_spec = build(BASE), spec(BASE)
report = {"base": BASE, "variants": {}}
for slug in VARIANTS:
    parts, s = build(slug), spec(slug)
    fields = [d for d in diff(base_spec, s) if not d.split(":")[0] in ("id", "slug", "name", "character.id", "character.slug", "character.name")]
    same = sorted(n for n in parts if n in base_parts and parts[n]["mesh_sha"] == base_parts[n]["mesh_sha"])
    changed = sorted(n for n in parts if n in base_parts and parts[n]["mesh_sha"] != base_parts[n]["mesh_sha"])
    added = sorted(set(parts) - set(base_parts))
    removed = sorted(set(base_parts) - set(parts))
    recolored = sorted(n for n in same if parts[n]["material"] != base_parts[n]["material"])
    profiles = {k: (base_spec.get(k), s.get(k)) for k in ("rig_profile", "animation_profile", "render_profile")}
    report["variants"][slug] = {
        "spec_changes": fields, "parts_identical": len(same), "parts_total": len(parts),
        "geometry_changed": changed, "added": added, "removed": removed, "material_changed": recolored,
        "profiles_identical": all(a == b for a, b in profiles.values()),
    }
(out / "modular.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
for slug, r in report["variants"].items():
    print(slug, "| campos:", r["spec_changes"][:3], "| iguais", r["parts_identical"], "/", r["parts_total"],
          "| geometria", r["geometry_changed"], "| +", r["added"], "| -", r["removed"], "| perfis iguais", r["profiles_identical"])

# Folha: linhas = personagens; colunas = S, SE, E, N (idle quadro 0), 2×.
dirs = ["S", "SE", "E", "N"]
C = 256
sheet = Image.new("RGB", (160 + C * len(dirs), C * (1 + len(VARIANTS))), (118, 150, 104))
draw = ImageDraw.Draw(sheet)
for r, slug in enumerate([BASE] + VARIANTS):
    render = latest(slug, "render")
    draw.text((6, r * C + C // 2), slug.replace("aprendiz_var_", "troca: ") if r else "base", fill=(20, 30, 20))
    for c, d in enumerate(dirs):
        im = Image.open(render / f"frames/idle/{d}/idle_{d}_0000.png").convert("RGBA").resize((C, C), Image.NEAREST)
        sheet.paste(im, (160 + c * C, r * C), im)
sheet.save(out / "variacoes.png")
