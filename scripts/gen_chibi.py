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


# ---------------------------------------------------------------- ações pontuais (poses-chave como dados)
STILL = {"stride_m": 0, "stance_fraction": 1, "foot_lift_m": 0, "pelvis_drop_m": 0, "pelvis_bob_m": 0,
         "arm_swing_deg": 0, "forearm_bend_deg": 0}
PLANTED = [(0, "LEFT_FOOT_CONTACT"), (0, "RIGHT_FOOT_CONTACT")]
REST_ARMS = {"forearm_l": (12, 0, 0), "forearm_r": (12, 0, 0)}


def key(t, pelvis=(0, 0, 0), **bones):
    return {"t": t, "bones": {**REST_ARMS, **bones}, "pelvis": pelvis}


def action(aid, category, fps, n, keys, events, phases, priority, interruptible_after, return_to, held=()):
    data = clip(aid, fps, n, 0.0, STILL, PLANTED + events)
    data.update({"loop": False, "category": category, "keys": keys, "priority": priority,
                 "interruptible_after": interruptible_after, "return_to": return_to, "held_frames": list(held),
                 "phases": [{"name": p, "start_frame": a, "end_frame": b} for p, a, b in phases]})
    return data


ACTIONS = [
    # Golpe de cajado: recua o braço (cajado inclina para trás) e varre para a frente.
    action("attack_melee", "melee", 12, 8, [
        key(0), key(.3, upper_arm_l=(-45, 0, 0), forearm_l=(25, 0, 0), chest=(4, 0, 18), spine_01=(6, 0, 0), head=(0, 0, 8)),
        key(.55, upper_arm_l=(80, 0, 0), forearm_l=(10, 0, 0), chest=(-6, 0, -22), spine_01=(-14, 0, 0), pelvis=(0, 0, -.01)),
        key(.75, upper_arm_l=(60, 0, 0), chest=(-4, 0, -14), spine_01=(-8, 0, 0)), key(1)],
        [(4, "HIT")], [("prepare", 0, 2), ("execute", 3, 4), ("recover", 5, 7)], 10, 5, "idle"),
    # Magia: ergue o cajado (preparo), estende para a frente (lançamento) e recolhe.
    action("cast", "magic", 12, 12, [
        key(0), key(.35, upper_arm_l=(110, 0, 0), forearm_l=(8, 0, 0), upper_arm_r=(55, 0, 0), forearm_r=(30, 0, 0),
                    chest=(5, 0, 0), head=(6, 0, 0)),
        key(.5, upper_arm_l=(115, 0, 0), forearm_l=(5, 0, 0), upper_arm_r=(60, 0, 0), forearm_r=(25, 0, 0), chest=(6, 0, 0), head=(8, 0, 0)),
        key(.62, upper_arm_l=(70, 0, 0), upper_arm_r=(75, 0, 0), forearm_r=(5, 0, 0), spine_01=(-7, 0, 0), chest=(-3, 0, 0)),
        key(1)],
        [(7, "CAST_RELEASE")], [("prepare", 0, 5), ("execute", 6, 7), ("recover", 8, 11)], 10, 8, "idle"),
    # Interação: inclina e alcança com a mão livre (direita), segura e volta.
    action("interact", "interaction", 10, 8, [
        key(0), key(.4, upper_arm_r=(65, 0, 0), forearm_r=(8, 0, 0), spine_01=(-18, 0, 0), head=(-10, 0, 0), pelvis=(0, 0, -.012)),
        key(.7, upper_arm_r=(62, 0, 0), forearm_r=(14, 0, 0), spine_01=(-16, 0, 0), head=(-8, 0, 0), pelvis=(0, 0, -.012)),
        key(1)],
        [(4, "INTERACT")], [("prepare", 0, 2), ("execute", 3, 5), ("recover", 6, 7)], 10, 6, "idle"),
    # Dano: recua o tronco e a cabeça, braços abrem para trás, volta.
    action("hurt", "state", 12, 6, [
        # Começa já no impacto (sem quadro neutro repetido), pico logo depois, volta ao neutro.
        key(0, spine_01=(8, 0, 0), chest=(5, 0, 4), head=(9, 0, 0), upper_arm_l=(-12, 0, 0), upper_arm_r=(-14, 0, 0),
               pelvis=(0, -.006, -.008)),
        key(.3, spine_01=(15, 0, 0), chest=(8, 0, 6), head=(17, 0, 0), upper_arm_l=(-24, 0, 0), upper_arm_r=(-28, 0, 0),
                pelvis=(0, -.012, -.016)),
        key(1)],
        [(0, "IMPACT")], [("execute", 0, 1), ("recover", 2, 5)], 20, 3, "idle"),
    # Morte: recua, cai de joelhos e tomba para a frente; os últimos quadros mantêm a pose.
    action("death", "state", 10, 10, [
        key(0), key(.2, spine_01=(12, 0, 0), head=(12, 0, 0), upper_arm_l=(-10, 0, 0), upper_arm_r=(-15, 0, 0)),
        # Braço do cajado estendido à frente (≈ 90° no mundo, somando o tronco inclinado): o cajado deita na altura da mão.
        key(.55, spine_01=(-22, 0, 0), chest=(-10, 0, 0), head=(-18, 0, 0), upper_arm_l=(112, 0, 0), forearm_l=(0, 0, 0),
                 upper_arm_r=(10, 0, 0), pelvis=(0, 0, -.06)),
        key(.8, spine_01=(-30, 0, 0), chest=(-14, 0, 0), head=(-26, 0, 0), upper_arm_l=(130, 0, 0), forearm_l=(0, 0, 0),
                upper_arm_r=(16, 0, 0), pelvis=(0, .006, -.09)),
        key(1, spine_01=(-30, 0, 0), chest=(-14, 0, 0), head=(-26, 0, 0), upper_arm_l=(130, 0, 0), forearm_l=(0, 0, 0),
                upper_arm_r=(16, 0, 0), pelvis=(0, .006, -.09))],
        [(8, "DEATH_REST")], [("execute", 0, 7), ("hold", 8, 9)], 100, 99, None, held=(9,)),
]


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
    ] + ACTIONS})

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
