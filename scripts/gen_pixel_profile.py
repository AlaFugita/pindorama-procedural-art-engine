"""Gera o perfil pindorama_pixel_art_detailed_v1, os perfis de render 192/256 e as fichas de teste."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "library"
SPECS = ROOT / "tests/fixtures/specs"


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def role(tones, lo, hi, shift=12.0, **extra):
    return {"tones": tones, "value_range": [lo, hi], "shadow_hue_shift_deg": shift, **extra}


ROLES = {
    "skin": role(4, .64, 1.0, -9.0, ao_strength=.45),
    "hair": role(4, .42, 1.0, 10.0, highlight="#F0B27A", highlight_threshold=.97, ao_strength=.6),
    "cloth": role(4, .42, 1.0, 16.0, ao_strength=.65),
    "cloth_pattern": role(4, .42, 1.0, 16.0, ao_strength=.65, pattern="glyph", pattern_scale=9.0),
    "cloth_light": role(3, .7, 1.0, 10.0, ao_strength=.4, pattern="stitch", pattern_scale=60.0),
    "leather": role(4, .45, 1.0, 8.0, ao_strength=.55, pattern="stitch", pattern_scale=45.0),
    "leather_dark": role(3, .4, .85, 8.0, ao_strength=.5),
    "wood": role(3, .5, 1.0, 8.0, ao_strength=.4, pattern="grain", pattern_scale=14.0),
    "metal": role(3, .55, 1.0, 20.0, base="#D9B35B", highlight="#FFF4C8", highlight_threshold=.8, ao_strength=.3),
    "gem": role(3, .7, 1.0, 0.0, highlight="#F4FFFF", highlight_threshold=.6, emissive=True, protect=True),
    "eyes": role(1, 1.0, 1.0, 0.0, shading=False, protect=True),
    "eye_shine": role(1, 1.0, 1.0, 0.0, shading=False, protect=True),
    "mouth": role(1, 1.0, 1.0, 0.0, shading=False, protect=True),
    "detail": role(2, .75, 1.0, 0.0, protect=True, ao_strength=.2),
    "ink": role(1, 1.0, 1.0, 0.0, shading=False, protect=True),
    "default": role(4, .45, 1.0, 12.0),
}
PART_ROLES = {
    "*": "default", "body": "skin", "head": "skin", "ear": "skin", "nose": "skin", "hand": "skin",
    "hair": "hair", "brows": "hair", "lashes": "ink",
    "eyes": "eyes", "iris": "eyes", "eye_white": "eyes", "eye_shine": "eye_shine", "mouth": "mouth", "blush": "detail",
    "hood": "cloth", "hair_locks": "hair", "boot_toe_": "leather", "lace_bracer_": "leather_dark", "hood_trim": "cloth_light", "hood_seam": "cloth_light", "cape": "cloth", "cape_trim": "cloth_light",
    "lapel": "cloth_light", "tunic": "cloth", "tunic_hem": "cloth_light", "sleeve_": "cloth", "sleeve_cuff_": "cloth_light",
    "vest": "leather", "collar": "cloth_light",
    "belt": "leather", "strap": "leather", "pouch": "leather", "bag": "leather", "bag_flap": "leather",
    "boot_": "leather", "boot_cuff_": "leather", "boot_sole_": "leather_dark", "lace_": "leather_dark",
    "bracer_": "leather", "wrap": "cloth_light",
    "staff": "wood", "staff_gem": "gem", "orb": "gem", "book": "leather", "book_clasp": "metal",
    "buckle": "metal", "hood_band": "metal", "clasp": "metal", "emblem": "metal", "stud": "metal", "bell": "metal",
}
chibi = json.loads((LIB / "profiles/art/pindorama_chibi_v1.json").read_text(encoding="utf-8"))
profile = copy.deepcopy(chibi)
profile.update({
    "id": "pindorama_pixel_art_detailed_v1", "version": "1.0.0", "light_shadows": True,
    "outline_thickness_m": 0.0, "outline_darken": .05,
    "lights": [
        {"name": "Key", "azimuth_deg": 215, "elevation_deg": 50, "energy": 2.6, "color": "#FFF4E2", "angle_deg": 6},
        {"name": "Fill", "azimuth_deg": 120, "elevation_deg": 20, "energy": .35, "color": "#C9DAFF", "angle_deg": 30},
    ],
    "world_strength": .1,
    "allowed_references": ["Mago e Coquinho do Pindorama", "Duende.png (nível de detalhe)"],
    "pixel": {
        "reference_canvas_px": 192, "light_bands": [.2, .42, .66], "roles": ROLES, "part_roles": PART_ROLES,
        "outline_mode": "outside", "outline_ink": "#1A1222", "outline_ink_mix": .6, "lit_outline_mix": .25,
        "internal_line_depth_m": .07, "cluster_min_px": 2, "glow_radius_px": 1, "alpha": "binary", "max_colors": 64,
    },
})
dump(LIB / "profiles/art/pindorama_pixel_art_detailed_v1.json", profile)

base = json.loads((LIB / "profiles/render/isometric_chibi_v1.json").read_text(encoding="utf-8"))
for size in (128, 192, 256):
    k = size / 128
    r = copy.deepcopy(base)
    r.update({"id": f"isometric_pixel_{size}_v1", "canvas": {"width": size, "height": size},
              "pixels_per_meter": round(104.0 * k, 3), "pivot": {"x": 64.0 * k, "y": 107.0 * k},
              "samples": 1, "filter_width_px": 0.01, "safety_margin_px": 2})
    dump(LIB / f"profiles/render/isometric_pixel_{size}_v1.json", r)

spec = json.loads((SPECS / "aprendiz_chibi.json").read_text(encoding="utf-8"))
for size in (128, 192, 256):
    s = copy.deepcopy(spec)
    s.update({"id": f"character_12{size // 64}", "slug": f"aprendiz_pixel_{size}", "name": f"Aprendiz pixel {size}",
              "art_profile": "pindorama_pixel_art_detailed_v1", "render_profile": f"isometric_pixel_{size}_v1"})
    dump(SPECS / f"aprendiz_pixel_{size}.json", s)

LICENSE = {"spdx_or_terms": "project-original", "origin": "blender/scripts/ics_blender/chibi_detail.py",
           "author": "Isometric Character Studio", "redistribution_allowed": True}
for aid, kind, gen, params, anchors in (
    ("chibi_face_detail_v1", "face", "chibi_face_detail", {"eye": "#5A3420", "brow": "#7A4326"}, ["head"]),
    ("chibi_hair_detail_v1", "hair", "chibi_hair_detail", {"color": "#A85B2C"}, ["head"]),
    ("chibi_robe_detail_v1", "outfit", "chibi_robe_detail", {}, ["chest"]),
    ("chibi_bag_detail_v1", "accessory", "chibi_bag_detail", {}, ["pelvis"]),
    ("chibi_staff_detail_v1", "weapon", "chibi_staff_detail", {"glow": "#FFD45A"}, ["hand_l"]),
):
    dump(LIB / "components" / aid / "asset.json", {
        "schema_version": "1.0.0", "id": aid, "version": "1.0.0", "kind": kind, "families": ["humanoid"],
        "generator": gen, "params": params, "anchors": anchors, "depends_on": [], "scale_reference_m": 1.0,
        "tags": ["detalhado"], "license": LICENSE})
for size in (128, 192, 256):
    s = copy.deepcopy(spec)
    s["appearance"].update({"hair_asset": "chibi_hair_detail_v1", "face_preset": "chibi_face_detail_v1"})
    s["outfit"].update({"body_asset": "chibi_robe_detail_v1", "accessories": ["chibi_bag_detail_v1"],
                        "weapon_asset": "chibi_staff_detail_v1"})
    s.update({"id": f"character_13{size // 64}", "slug": f"aprendiz_detalhado_{size}", "name": f"Aprendiz detalhado {size}",
              "art_profile": "pindorama_pixel_art_detailed_v1", "render_profile": f"isometric_pixel_{size}_v1"})
    dump(SPECS / f"aprendiz_detalhado_{size}.json", s)
s = copy.deepcopy(spec)
s["appearance"].update({"hair_asset": "chibi_hair_detail_v1", "face_preset": "chibi_face_detail_v1"})
s["outfit"].update({"body_asset": "chibi_robe_detail_v1", "accessories": ["chibi_bag_detail_v1"], "weapon_asset": "chibi_staff_detail_v1"})
s.update({"id": "character_140", "slug": "aprendiz_detalhado_suave", "name": "Aprendiz detalhado suave"})
dump(SPECS / "aprendiz_detalhado_suave.json", s)

# ---------------------------------------------------------------- perfil principal: ilustração suave
SMOOTH_ROLES = copy.deepcopy(ROLES)
for name, data in SMOOTH_ROLES.items():
    if data.get("shading", True) and not data.get("emissive"):
        data["tones"] = max(data["tones"], 4)
SMOOTH_ROLES["skin"].update({"value_range": [.7, 1.05], "shadow_hue_shift_deg": -12.0, "ao_strength": .35})
SMOOTH_ROLES["cloth"].update({"value_range": [.44, 1.1], "ao_strength": .55})
SMOOTH_ROLES["cloth_pattern"].update({"value_range": [.44, 1.1], "ao_strength": .55})
SMOOTH_ROLES["hair"].update({"value_range": [.5, 1.05], "highlight_threshold": .9})
SMOOTH_ROLES["metal"].update({"highlight_threshold": .7})
smooth = copy.deepcopy(profile)
smooth.pop("pixel")
smooth.update({
    "id": "pindorama_friendly_smooth_v1", "version": "1.0.0",
    "allowed_references": ["Mago e Coquinho (identidade)", "Duende.png (nível de detalhe)", "Saci.png (expressividade)"],
    "lights": [
        {"name": "Key", "azimuth_deg": 215, "elevation_deg": 50, "energy": 2.7, "color": "#FFF2DD", "angle_deg": 14},
        {"name": "Fill", "azimuth_deg": 120, "elevation_deg": 20, "energy": .4, "color": "#CBDBFF", "angle_deg": 40},
    ],
    "smooth": {
        "reference_canvas_px": 192, "supersample": 3, "light_bands": [.2, .45, .72], "band_softness": .14,
        "roles": SMOOTH_ROLES, "part_roles": PART_ROLES, "texture_strength": .3,
        "outline_px": 1.6, "outline_shadow_extra_px": .9, "shadow_side": [.6, .8],
        "outline_ink": "#2A1E2E", "outline_ink_mix": .5,
        "internal_line_px": .9, "internal_line_depth_m": .07, "internal_line_strength": .75,
        "glow_radius_px": 5.0, "glow_strength": .55,
        "noise_strength": .32, "rim_px": 2.0, "rim_strength": .5, "rim_color": "#FFF2D8",
    },
})
dump(LIB / "profiles/art/pindorama_friendly_smooth_v1.json", smooth)
for size in (192, 256):
    k = size / 128
    r = copy.deepcopy(base)
    r.update({"id": f"isometric_smooth_{size}_v1", "canvas": {"width": size, "height": size},
              "pixels_per_meter": round(104.0 * k, 3), "pivot": {"x": 64.0 * k, "y": 107.0 * k},
              "samples": 16, "filter_width_px": 1.0, "safety_margin_px": 2})
    dump(LIB / f"profiles/render/isometric_smooth_{size}_v1.json", r)
    s = copy.deepcopy(spec)
    s["appearance"].update({"hair_asset": "chibi_hair_detail_v1", "face_preset": "chibi_face_detail_v1"})
    s["outfit"].update({"body_asset": "chibi_robe_detail_v1", "accessories": ["chibi_bag_detail_v1"],
                        "weapon_asset": "chibi_staff_detail_v1"})
    s["appearance"]["face_preset"] = "chibi_face_decal_v1"
    s.update({"id": f"character_15{size // 64}", "slug": f"aprendiz_suave_{size}", "name": f"Aprendiz suave {size}",
              "art_profile": "pindorama_friendly_smooth_v1", "render_profile": f"isometric_smooth_{size}_v1"})
    dump(SPECS / f"aprendiz_suave_{size}.json", s)

dump(LIB / "components/chibi_face_decal_v1/asset.json", {
    "schema_version": "1.0.0", "id": "chibi_face_decal_v1", "version": "1.0.0", "kind": "face", "families": ["humanoid"],
    "generator": "chibi_face_decal", "params": {"eye": "#2A1A14", "iris": "#7A4A2A", "brow": "#6B3A20", "mouth": "#8C3B32"},
    "anchors": ["head"], "depends_on": [], "scale_reference_m": 1.0, "tags": ["rosto", "decalque", "vetorial"],
    "license": {"spdx_or_terms": "project-original", "origin": "blender/scripts/ics_blender/face_decal.py",
                "author": "Isometric Character Studio", "redistribution_allowed": True}})
print("ok")
