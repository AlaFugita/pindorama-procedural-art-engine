"""Gera library/rigs/humanoid_standard_v1/rig.json. Esquerda anatômica = -X (doc 17 §2)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bones = []


def bone(name, parent, side, role, deform, head, tail, connected=False, roll=0.0):
    bones.append({
        "semantic_id": name, "blender_name": name, "side": side, "role": role,
        "parent": parent, "deform": deform, "head": head, "tail": tail,
        "roll_deg": roll, "connected": connected, "required": True,
    })


bone("root", None, "CENTER", "root", False, (0, 0, 0), (0, 0.12, 0))
bone("pelvis", "root", "CENTER", "pelvis", True, (0, 0, .50), (0, 0, .58))
bone("spine_01", "pelvis", "CENTER", "spine", True, (0, 0, .58), (0, 0, .68), True)
bone("chest", "spine_01", "CENTER", "chest", True, (0, 0, .68), (0, 0, .80), True)
bone("neck", "chest", "CENTER", "neck", True, (0, 0, .80), (0, 0, .86), True)
bone("head", "neck", "CENTER", "head", True, (0, 0, .86), (0, 0, 1.24), True)
bone("qa_front", "root", "NONE", "qa_marker", False, (0, .35, .60), (0, .45, .60))

for s, sign, side in (("l", -1, "LEFT"), ("r", 1, "RIGHT")):
    bone(f"clavicle_{s}", "chest", side, "clavicle", True,
         (sign * .03, 0, .78), (sign * .125, 0, .775))
    bone(f"upper_arm_{s}", f"clavicle_{s}", side, "upper_arm", True,
         (sign * .125, 0, .775), (sign * .235, 0, .60), True)
    bone(f"forearm_{s}", f"upper_arm_{s}", side, "forearm", True,
         (sign * .235, 0, .60), (sign * .30, .02, .445), True)
    bone(f"hand_{s}", f"forearm_{s}", side, "hand", True,
         (sign * .30, .02, .445), (sign * .325, .03, .375), True)
    bone(f"thigh_{s}", "pelvis", side, "upper_leg", True,
         (sign * .085, 0, .50), (sign * .085, .012, .29))
    bone(f"shin_{s}", f"thigh_{s}", side, "lower_leg", True,
         (sign * .085, .012, .29), (sign * .085, 0, .085), True)
    bone(f"foot_{s}", f"shin_{s}", side, "foot", True,
         (sign * .085, 0, .085), (sign * .085, .095, .03), True)
    bone(f"toe_{s}", f"foot_{s}", side, "toe", True,
         (sign * .085, .095, .03), (sign * .085, .16, .03), True)
    bone(f"heel_{s}", f"foot_{s}", side, "contact_heel", False,
         (sign * .085, -.04, 0), (sign * .085, -.04, .04))
    bone(f"ball_{s}", f"foot_{s}", side, "contact_ball", False,
         (sign * .085, .14, 0), (sign * .085, .14, .04))
    bone(f"ctrl_foot_{s}", "root", side, "ik_control", False,
         (sign * .085, 0, .085), (sign * .085, .1, .085))
    bone(f"ik_foot_{s}", f"ctrl_foot_{s}", side, "ik_target", False,
         (sign * .085, 0, .085), (sign * .085, .095, .03))
    bone(f"pole_knee_{s}", "root", side, "ik_pole", False,
         (sign * .085, .4, .29), (sign * .085, .5, .29))

STATIC_ALL = ["hand_l", "hand_r", "foot_l", "foot_r", "head"]


def without(*names):
    return [n for n in STATIC_ALL if n not in names]


sentinels = [
    {"id": "leg_left", "bone": "ctrl_foot_l", "mode": "translate", "vector": (0, .1, .1),
     "expected_moved": ["foot_l", "shin_l", "toe_l"], "expected_static": without("foot_l")},
    {"id": "leg_right", "bone": "ctrl_foot_r", "mode": "translate", "vector": (0, .1, .1),
     "expected_moved": ["foot_r", "shin_r", "toe_r"], "expected_static": without("foot_r")},
    {"id": "arm_left", "bone": "upper_arm_l", "mode": "rotate", "vector": (45, 0, 0),
     "expected_moved": ["forearm_l", "hand_l"], "expected_static": without("hand_l")},
    {"id": "arm_right", "bone": "upper_arm_r", "mode": "rotate", "vector": (45, 0, 0),
     "expected_moved": ["forearm_r", "hand_r"], "expected_static": without("hand_r")},
    {"id": "head", "bone": "head", "mode": "rotate", "vector": (20, 0, 30),
     "expected_moved": ["head"], "expected_static": without("head")},
    {"id": "spine", "bone": "spine_01", "mode": "rotate", "vector": (20, 0, 0),
     "expected_moved": ["chest", "head", "hand_l", "hand_r"],
     "expected_static": ["foot_l", "foot_r"]},
]

profile = {
    "schema_version": "1.0.0", "id": "humanoid_standard_v1", "version": "1.0.0",
    "family": "humanoid", "reference_height_m": 1.3,
    "orientation": "+Z_up,+Y_front,+X_right_anatomical",
    "max_influences": 4, "weight_sum_tolerance": 0.001, "side_center_tolerance_m": 0.005,
    "compatible_animation_profiles": ["humanoid_basic_v1"],
    "ik_chains": {
        f"leg_{s}": {"tip": f"shin_{s}", "target": f"ik_foot_{s}", "pole": f"pole_knee_{s}",
                     "foot": f"foot_{s}", "base": f"thigh_{s}"} for s in "lr"
    },
    "bones": bones, "sentinel_poses": sentinels,
}
out = ROOT / "library/rigs/humanoid_standard_v1"
out.mkdir(parents=True, exist_ok=True)
(out / "rig.json").write_text(json.dumps(profile, indent=1) + "\n", encoding="utf-8")
print(len(bones), "ossos")
