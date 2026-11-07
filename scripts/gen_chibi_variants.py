"""Cria os assets alternativos e cinco fichas que diferem do Aprendiz em UM campo cada.

Teste de personalização modular: capuz, cabelo, roupa, acessório e arma.
"""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "library"
SPECS = ROOT / "tests/fixtures/specs"
LICENSE = {"spdx_or_terms": "project-original", "origin": "blender/scripts/ics_blender/chibi_components.py",
           "author": "Isometric Character Studio", "redistribution_allowed": True}


def asset(aid, kind, gen, params, anchors, tags):
    folder = LIB / "components" / aid
    folder.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": "1.0.0", "id": aid, "version": "1.0.0", "kind": kind, "families": ["humanoid"],
            "generator": gen, "params": params, "anchors": anchors, "depends_on": [], "scale_reference_m": 1.0,
            "tags": tags, "license": LICENSE}
    (folder / "asset.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


asset("chibi_hair_swept_v1", "hair", "chibi_hair", {"color": "#A85B2C", "style": "swept"}, ["head"], ["cabelo", "franja lateral"])
asset("chibi_robe_vest_v1", "outfit", "chibi_robe", {"hood": False, "cape": False}, ["chest"], ["roupa", "colete"])
asset("chibi_book_v1", "accessory", "chibi_book", {}, ["pelvis"], ["grimório"])
asset("chibi_crystal_staff_v1", "weapon", "chibi_crystal_staff", {"gem": "#6FD3E6"}, ["hand_l"], ["cajado", "cristal"])

base = json.loads((SPECS / "aprendiz_chibi.json").read_text(encoding="utf-8"))
variants = {
    "capuz": ("palette", "primary", "#A8433A"),
    "cabelo": ("appearance", "hair_asset", "chibi_hair_swept_v1"),
    "roupa": ("outfit", "body_asset", "chibi_robe_vest_v1"),
    "acessorio": ("outfit", "accessories", ["chibi_book_v1"]),
    "arma": ("outfit", "weapon_asset", "chibi_crystal_staff_v1"),
}
for n, (name, (section, field, value)) in enumerate(variants.items(), start=1):
    spec = copy.deepcopy(base)
    spec[section][field] = value
    spec["id"] = f"character_{110 + n}"
    spec["slug"] = f"aprendiz_var_{name}"
    spec["name"] = f"Aprendiz variação {name}"
    (SPECS / f"aprendiz_var_{name}.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(spec["slug"], section, field, value)
