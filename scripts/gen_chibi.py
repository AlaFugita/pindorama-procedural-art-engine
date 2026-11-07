"""Gera a família chibi: rig, animações, perfis, assets e o Aprendiz (Mago).

Alvo: DIRECAO-DE-ARTE.md do Pindorama. Chibi 2.5D na linha de Ragnarok Online, desenho liso,
contorno grosso, poucos detalhes. Medidas em metros, altura de referência 1,0 (~2,3 cabeças).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "library"
bones = []


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def bone(name, parent, side, role, deform, head, tail, connected=False):
    bones.append({"semantic_id": name, "blender_name": name, "side": side, "role": role,
                  "parent": parent, "deform": deform, "head": head, "tail": tail,
                  "roll_deg": 0.0, "connected": connected, "required": True})


bone("root", None, "CENTER", "root", False, (0, 0, 0), (0, .1, 0))
bone("pelvis", "root", "CENTER", "pelvis", True, (0, 0, .30), (0, 0, .36))
bone("spine_01", "pelvis", "CENTER", "spine", True, (0, 0, .36), (0, 0, .42), True)
bone("chest", "spine_01", "CENTER", "chest", True, (0, 0, .42), (0, 0, .50), True)
bone("neck", "chest", "CENTER", "neck", True, (0, 0, .50), (0, 0, .54), True)
bone("head", "neck", "CENTER", "head", True, (0, 0, .54), (0, 0, 1.0), True)
bone("qa_front", "root", "NONE", "qa_marker", False, (0, .3, .4), (0, .4, .4))
for s, k, side in (("l", -1, "LEFT"), ("r", 1, "RIGHT")):
    bone(f"clavicle_{s}", "chest", side, "clavicle", True, (k * .03, 0, .50), (k * .105, 0, .495))
    bone(f"upper_arm_{s}", f"clavicle_{s}", side, "upper_arm", True,
         (k * .105, 0, .495), (k * .165, 0, .40), True)
    bone(f"forearm_{s}", f"upper_arm_{s}", side, "forearm", True,
         (k * .165, 0, .40), (k * .205, .012, .31), True)
    bone(f"hand_{s}", f"forearm_{s}", side, "hand", True,
         (k * .205, .012, .31), (k * .222, .018, .25), True)
    bone(f"thigh_{s}", "pelvis", side, "upper_leg", True, (k * .07, 0, .30), (k * .07, .01, .19))
    bone(f"shin_{s}", f"thigh_{s}", side, "lower_leg", True,
         (k * .07, .01, .19), (k * .07, 0, .07), True)
    bone(f"foot_{s}", f"shin_{s}", side, "foot", True, (k * .07, 0, .07), (k * .07, .08, .025), True)
    bone(f"toe_{s}", f"foot_{s}", side, "toe", True, (k * .07, .08, .025), (k * .07, .13, .025), True)
    bone(f"heel_{s}", f"foot_{s}", side, "contact_heel", False, (k * .07, -.035, 0), (k * .07, -.035, .03))
    bone(f"ball_{s}", f"foot_{s}", side, "contact_ball", False, (k * .07, .115, 0), (k * .07, .115, .03))
    bone(f"ctrl_foot_{s}", "root", side, "ik_control", False, (k * .07, 0, .07), (k * .07, .08, .07))
    bone(f"ik_foot_{s}", f"ctrl_foot_{s}", side, "ik_target", False, (k * .07, 0, .07), (k * .07, .08, .025))
    bone(f"pole_knee_{s}", "root", side, "ik_pole", False, (k * .07, .3, .19), (k * .07, .38, .19))

ALL = ["hand_l", "hand_r", "foot_l", "foot_r", "head"]


def rest(*names):
    return [n for n in ALL if n not in names]


sentinels = [
    {"id": "leg_left", "bone": "ctrl_foot_l", "mode": "translate", "vector": (0, .06, .06),
     "expected_moved": ["foot_l", "shin_l", "toe_l"], "expected_static": rest("foot_l")},
    {"id": "leg_right", "bone": "ctrl_foot_r", "mode": "translate", "vector": (0, .06, .06),
     "expected_moved": ["foot_r", "shin_r", "toe_r"], "expected_static": rest("foot_r")},
    {"id": "arm_left", "bone": "upper_arm_l", "mode": "rotate", "vector": (45, 0, 0),
     "expected_moved": ["forearm_l", "hand_l"], "expected_static": rest("hand_l")},
    {"id": "arm_right", "bone": "upper_arm_r", "mode": "rotate", "vector": (45, 0, 0),
     "expected_moved": ["forearm_r", "hand_r"], "expected_static": rest("hand_r")},
    {"id": "head", "bone": "head", "mode": "rotate", "vector": (20, 0, 30),
     "expected_moved": ["head"], "expected_static": rest("head")},
    {"id": "spine", "bone": "spine_01", "mode": "rotate", "vector": (20, 0, 0),
     "expected_moved": ["chest", "head", "hand_l", "hand_r"], "expected_static": ["foot_l", "foot_r"]},
]
dump(LIB / "rigs/humanoid_chibi_v1/rig.json", {
    "schema_version": "1.0.0", "id": "humanoid_chibi_v1", "version": "1.0.0", "family": "humanoid",
    "reference_height_m": 1.0, "orientation": "+Z_up,+Y_front,+X_right_anatomical",
    "max_influences": 4, "weight_sum_tolerance": .001, "side_center_tolerance_m": .005,
    "compatible_animation_profiles": ["humanoid_chibi_basic_v1"],
    "ik_chains": {f"leg_{s}": {"tip": f"shin_{s}", "target": f"ik_foot_{s}", "pole": f"pole_knee_{s}",
                               "foot": f"foot_{s}", "base": f"thigh_{s}"} for s in "lr"},
    "bones": bones, "sentinel_poses": sentinels,
})

TOL = {"foot_slide_speed_h_per_s": .03, "ground_penetration_h": .006, "contact_height_h": .012,
       "ik_error_h": .002, "max_landmark_step_h": .32, "loop_landmark_gap_factor": 1.25}


def clip(aid, fps, n, speed, gait, events):
    return {"animation_id": aid, "version": "1.0.0", "fps": fps, "frame_count": n, "loop": True,
            "root_motion": "in_place", "ground_speed_mps": speed, "gait": gait,
            "events": [{"frame": f, "event": e} for f, e in events], "tolerances": TOL,
            "approval": "UNAPPROVED"}


dump(LIB / "animations/humanoid_chibi_basic_v1.json", {
    "schema_version": "1.0.0", "id": "humanoid_chibi_basic_v1", "version": "1.0.0",
    "rig_profile": "humanoid_chibi_v1", "clips": [
        clip("idle", 8, 8, 0.0, {"stride_m": 0, "stance_fraction": 1, "foot_lift_m": 0, "pelvis_drop_m": .012,
                                 "pelvis_bob_m": .009, "arm_swing_deg": 5, "forearm_bend_deg": 12},
             [(0, "LEFT_FOOT_CONTACT"), (0, "RIGHT_FOOT_CONTACT")]),
        clip("walk", 12, 8, round(.17 / (8 / 12 * 5 / 8), 4),
             {"stride_m": .17, "stance_fraction": .625, "foot_lift_m": .035, "pelvis_drop_m": .018,
              "pelvis_bob_m": .006, "arm_swing_deg": 26, "forearm_bend_deg": 16, "torso_lean_deg": 3,
              "torso_twist_deg": 5},
             [(0, "LEFT_FOOT_CONTACT"), (5, "LEFT_SWING"), (4, "RIGHT_FOOT_CONTACT"), (1, "RIGHT_SWING")]),
        clip("run", 16, 8, round(.19 / (8 / 16 * 3 / 8), 4),
             {"stride_m": .19, "stance_fraction": .375, "foot_lift_m": .045, "pelvis_drop_m": .04,
              "pelvis_bob_m": .009, "arm_swing_deg": 40, "forearm_bend_deg": 50, "torso_lean_deg": 9,
              "torso_twist_deg": 9},
             [(0, "LEFT_FOOT_CONTACT"), (3, "LEFT_SWING"), (4, "RIGHT_FOOT_CONTACT"), (7, "RIGHT_SWING")]),
    ]})

dump(LIB / "profiles/render/isometric_chibi_v1.json", {
    "schema_version": "1.0.0", "id": "isometric_chibi_v1", "version": "1.0.0", "projection": "orthographic",
    "elevation_deg": 30.0, "azimuth_deg": 0.0, "canvas": {"width": 128, "height": 128},
    "pixels_per_meter": 104.0, "pivot": {"x": 64.0, "y": 107.0}, "safety_margin_px": 2,
    "engine": "BLENDER_EEVEE", "samples": 32, "filter_width_px": 1.1, "view_transform": "Standard",
    "rotation_strategy": "rotate_character_root",
    "direction_order": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    "headings_deg": {"N": 0, "NE": 45, "E": 90, "SE": 135, "S": 180, "SW": 225, "W": 270, "NW": 315},
})
dump(LIB / "profiles/art/pindorama_chibi_v1.json", {
    "schema_version": "1.0.0", "id": "pindorama_chibi_v1", "version": "1.0.0", "reference_height_m": 1.0,
    "lights": [
        {"name": "Key", "azimuth_deg": 195, "elevation_deg": 52, "energy": 2.7, "color": "#FFFFFF", "angle_deg": 10},
        {"name": "Fill", "azimuth_deg": 130, "elevation_deg": 20, "energy": .25, "color": "#FFFFFF", "angle_deg": 30},
    ],
    "world_color": "#FFFFFF", "world_strength": .12,
    "toon_steps": [[0.0, .68], [.34, .86], [.5, 1.0]],
    "light_shadows": False, "outline_thickness_m": .017, "outline_darken": .055, "allowed_references": ["Mago e Coquinho do Pindorama"],
})
LICENSE = {"spdx_or_terms": "project-original", "origin": "blender/scripts/ics_blender/chibi_components.py",
           "author": "Isometric Character Studio", "redistribution_allowed": True}
for aid, kind, gen, params, anchors, tags in (
    ("chibi_body_v1", "body", "chibi_body", {}, ["root"], ["corpo", "chibi"]),
    ("chibi_head_v1", "head", "chibi_head", {}, ["head"], ["cabeça", "chibi"]),
    ("chibi_face_v1", "face", "chibi_face", {"eye": "#3A2418"}, ["head"], ["rosto", "chibi"]),
    ("chibi_hair_bangs_v1", "hair", "chibi_hair", {"color": "#A85B2C"}, ["head"], ["cabelo"]),
    ("chibi_robe_v1", "outfit", "chibi_robe", {}, ["chest"], ["roupa", "capuz"]),
    ("chibi_bag_v1", "accessory", "chibi_bag", {}, ["pelvis"], ["bolsa"]),
    ("chibi_staff_v1", "weapon", "chibi_staff", {}, ["hand_l"], ["cajado", "aprendiz"]),
    ("chibi_skin_01", "material", "material_skin", {"base": "#F4C79A"}, [], ["pele"]),
):
    folder = LIB / ("materials" if kind == "material" else "components") / aid
    dump(folder / "asset.json", {
        "schema_version": "1.0.0", "id": aid, "version": "1.0.0", "kind": kind, "families": ["humanoid"],
        "generator": gen, "params": params, "anchors": anchors, "depends_on": [], "scale_reference_m": 1.0,
        "tags": tags, "license": LICENSE})


def spec(cid, name, slug, primary):
    return {"schema_version": "1.0.0", "id": cid, "name": name, "slug": slug, "family": "humanoid",
            "art_profile": "pindorama_chibi_v1",
            "body_profile": {"asset_id": "chibi_body_v1", "scale": 1.0, "proportions": "chibi_round"},
            "appearance": {"head_asset": "chibi_head_v1", "hair_asset": "chibi_hair_bangs_v1",
                           "skin_material": "chibi_skin_01", "face_preset": "chibi_face_v1"},
            "outfit": {"body_asset": "chibi_robe_v1", "accessories": ["chibi_bag_v1"], "weapon_asset": "chibi_staff_v1"},
            "palette": {"primary": primary, "secondary": "#8A5230", "accent": "#EFDFB8"},
            "rig_profile": "humanoid_chibi_v1", "animation_profile": "humanoid_chibi_basic_v1",
            "render_profile": "isometric_chibi_v1"}


dump(ROOT / "tests/fixtures/specs/aprendiz_chibi.json", spec("character_101", "Aprendiz", "aprendiz", "#5C72AE"))
dump(ROOT / "tests/fixtures/specs/aprendiz_floresta.json", spec("character_102", "Aprendiz da Floresta", "aprendiz_floresta", "#4F8A5B"))
print(len(bones), "ossos")
