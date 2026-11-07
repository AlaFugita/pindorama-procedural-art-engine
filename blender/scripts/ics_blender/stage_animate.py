"""Grava os clips no .blend aberto e registra a pista de todos os frames (ANI-001)."""

import math

import bpy

from . import animation as anim
from . import rig as rig_utils

LANDMARKS = [
    "root", "pelvis", "head", "hand_l", "hand_r", "foot_l", "foot_r", "heel_l", "heel_r",
    "ball_l", "ball_r", "ik_foot_l", "ik_foot_r", "thigh_l", "thigh_r", "shin_l", "shin_r",
]


def _finite(armature):
    for bone in armature.pose.bones:
        for row in bone.matrix:
            for value in row:
                if not math.isfinite(value):
                    return False
    return True


def trace_clip(armature, clip):
    scene = bpy.context.scene
    frames = []
    for frame in range(clip["frame_count"] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        points = {
            name: rig_utils.vec(rig_utils.bone_world(armature, name)) for name in LANDMARKS
        }
        frames.append({"frame": frame, "finite": _finite(armature), "points": points})
    return frames


def run(payload):
    armature = bpy.data.objects["ICS_Rig"]
    factor = payload.get("right_arm_factor", 1.0)
    anim.FOOT = tuple(payload.get("foot", anim.FOOT))
    anim.WEAPON_SIDE = payload.get("weapon_side", "r")
    traces = {}
    for clip in payload["clips"]:
        anim.bake_clip(armature, clip, factor)
        traces[clip["animation_id"]] = trace_clip(armature, clip)
    bpy.ops.wm.save_mainfile(filepath=payload["blend_path"], compress=True)
    return {
        "clips": sorted(traces),
        "traces": traces,
        "actions": sorted(a.name for a in bpy.data.actions),
    }
