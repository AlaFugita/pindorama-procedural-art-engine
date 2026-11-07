"""Gera asset.json dos componentes e o perfil de animação.

Todos os assets são geométricos e procedurais, escritos neste projeto: nenhum arquivo de
terceiro entra na biblioteca.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "library"
LICENSE = {
    "spdx_or_terms": "project-original",
    "origin": "gerado por blender/scripts/ics_blender/components.py",
    "author": "Isometric Character Studio",
    "redistribution_allowed": True,
}
ASSETS = [
    ("humanoid_compact_v1", "body", "body_compact", {}, ["root"], ["corpo", "chibi"]),
    ("head_round_v1", "head", "head", {"rx": .205, "ry": .19, "rz": .2, "chin": .78},
     ["head"], ["cabeça", "redonda"]),
    ("head_long_v1", "head", "head", {"rx": .18, "ry": .18, "rz": .215, "chin": .62},
     ["head"], ["cabeça", "alongada"]),
    ("hair_long_tied_v1", "hair", "hair_long_tied", {}, ["head"], ["cabelo", "longo", "preso"]),
    ("hair_short_spiky_v1", "hair", "hair_short_spiky", {}, ["head"], ["cabelo", "curto"]),
    ("hair_bun_v1", "hair", "hair_bun", {}, ["head"], ["cabelo", "coque"]),
    ("face_guardian_01", "face", "face", {"eye": "#2B2118", "brow": "#2B1A12", "angry": .25},
     ["head"], ["rosto", "sério"]),
    ("face_calm_01", "face", "face", {"eye": "#23405A", "brow": "#3A2A20", "angry": -.1},
     ["head"], ["rosto", "calmo"]),
    ("outfit_natural_fabric_01", "outfit", "outfit_tunic", {"hem": .32, "flare": .05},
     ["chest", "pelvis"], ["roupa", "túnica", "tecido"]),
    ("outfit_leather_armor_01", "outfit", "outfit_armor", {"hem": .40, "flare": .03},
     ["chest", "pelvis"], ["roupa", "armadura", "couro"]),
    ("outfit_robe_01", "outfit", "outfit_tunic", {"hem": .22, "flare": .09, "long_sash": True},
     ["chest", "pelvis"], ["roupa", "manto"]),
    ("feather_ornament_01", "accessory", "acc_feathers", {}, ["head"],
     ["acessório", "pena", "assimétrico"]),
    ("necklace_01", "accessory", "acc_necklace", {}, ["chest"], ["acessório", "colar"]),
    ("shoulder_guard_01", "accessory", "acc_shoulder_guard", {}, ["clavicle_l"],
     ["acessório", "ombreira", "assimétrico"]),
    ("belt_pouch_01", "accessory", "acc_pouch", {}, ["pelvis"],
     ["acessório", "bolsa", "assimétrico"]),
    ("spear_wood_01", "weapon", "weapon_spear", {}, ["hand_r"], ["arma", "lança"]),
    ("sword_iron_01", "weapon", "weapon_sword", {}, ["hand_r"], ["arma", "espada"]),
    ("staff_stone_01", "weapon", "weapon_staff", {}, ["hand_r"], ["arma", "cajado"]),
]
for sid, base in (("skin_warm_01", "#C98A5E"), ("skin_light_01", "#E8BE9C"), ("skin_deep_01", "#7A4A30")):
    ASSETS.append((sid, "material", "material_skin", {"base": base}, [], ["pele"]))

for aid, kind, gen, params, anchors, tags in ASSETS:
    folder = ROOT / ("materials" if kind == "material" else "components") / aid
    folder.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "1.0.0", "id": aid, "version": "1.0.0", "kind": kind,
        "families": ["humanoid"], "generator": gen, "params": params, "anchors": anchors,
        "depends_on": [], "scale_reference_m": 1.3, "tags": tags, "license": LICENSE,
    }
    text = json.dumps(meta, indent=2, ensure_ascii=False) + "\n"
    (folder / "asset.json").write_text(text, encoding="utf-8")

# Tolerâncias em fração da altura de referência; calibradas no primeiro rig (doc 18 §3.2).
TOL = {
    "foot_slide_speed_h_per_s": .03, "ground_penetration_h": .006, "contact_height_h": .012,
    "ik_error_h": .002, "max_landmark_step_h": .32, "loop_landmark_gap_factor": 1.25,
}


def clip(aid, fps, n, speed, gait, events):
    return {
        "animation_id": aid, "version": "1.0.0", "fps": fps, "frame_count": n, "loop": True,
        "root_motion": "in_place", "ground_speed_mps": speed, "gait": gait,
        "events": [{"frame": f, "event": e} for f, e in events], "tolerances": TOL,
        "approval": "UNAPPROVED",
    }


anim = {
    "schema_version": "1.0.0", "id": "humanoid_basic_v1", "version": "1.0.0",
    "rig_profile": "humanoid_standard_v1",
    "clips": [
        clip("idle", 8, 8, 0.0,
             {"stride_m": 0, "stance_fraction": 1, "foot_lift_m": 0, "pelvis_drop_m": .018,
              "pelvis_bob_m": .006, "arm_swing_deg": 2.5, "forearm_bend_deg": 10},
             [(0, "LEFT_FOOT_CONTACT"), (0, "RIGHT_FOOT_CONTACT")]),
        clip("walk", 12, 8, round(.30 / (8 / 12 * 5 / 8), 4),
             {"stride_m": .30, "stance_fraction": .625, "foot_lift_m": .05, "pelvis_drop_m": .035,
              "pelvis_bob_m": .008, "arm_swing_deg": 24, "forearm_bend_deg": 16,
              "torso_lean_deg": 3, "torso_twist_deg": 6},
             [(0, "LEFT_FOOT_CONTACT"), (5, "LEFT_SWING"), (4, "RIGHT_FOOT_CONTACT"),
              (1, "RIGHT_SWING")]),
        clip("run", 16, 8, round(.40 / (8 / 16 * 3 / 8), 4),
             {"stride_m": .40, "stance_fraction": .375, "foot_lift_m": .10, "pelvis_drop_m": .07,
              "pelvis_bob_m": .012, "arm_swing_deg": 42, "forearm_bend_deg": 60,
              "torso_lean_deg": 10, "torso_twist_deg": 12},
             [(0, "LEFT_FOOT_CONTACT"), (3, "LEFT_SWING"), (4, "RIGHT_FOOT_CONTACT"),
              (7, "RIGHT_SWING")]),
    ],
}
(ROOT / "animations").mkdir(exist_ok=True)
text = json.dumps(anim, indent=2) + "\n"
(ROOT / "animations/humanoid_basic_v1.json").write_text(text, encoding="utf-8")
print(len(ASSETS), "assets")
