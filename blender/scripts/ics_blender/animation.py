"""Clips procedurais idle/walk/run sobre o rig: dados estruturados, não mão livre.

Convenção "em esteira" (root_motion=in_place): o root fica na origem e o pé de apoio recua em
velocidade constante. No mundo, com o root andando à ``ground_speed_mps``, o pé fica plantado.
Fase 0 = pé esquerdo tocando o chão à frente.
"""

import math

import bpy

from . import rig as rig_utils


def _foot_pose(phase, gait):
    """(y, z_extra, pitch_graus) do tornozelo para a fase do pé em [0, 1)."""
    stride, stance = gait["stride_m"], gait["stance_fraction"]
    if stance >= 1.0 or stride == 0:
        return 0.0, 0.0, 0.0
    if phase < stance:
        return stride / 2 - stride * (phase / stance), 0.0, 0.0
    u = (phase - stance) / (1 - stance)
    ease = u * u * (3 - 2 * u)
    y = -stride / 2 + stride * ease
    lift = gait["foot_lift_m"] * math.sin(math.pi * u)
    pitch = -28.0 * math.sin(2 * math.pi * u) * min(1.0, gait["foot_lift_m"] / .05)
    return y, lift, pitch


# Geometria do pé do rig ativo: (calcanhar y, ponta y, altura do tornozelo).
FOOT = (-.04, .14, .085)
WEAPON_SIDE = "r"


def _sole_clearance(pitch_deg):
    """Quanto erguer o tornozelo para calcanhar e ponta não entrarem no chão."""
    rad = math.radians(pitch_deg)
    heel, ball, ankle = FOOT
    lowest = 0.0
    for y in (heel, ball):
        lowest = min(lowest, y * math.sin(rad) - ankle * math.cos(rad) + ankle)
    return -lowest


def _smooth(u):
    return u * u * (3 - 2 * u)


def apply_keys(armature, keys, t):
    """Ação por poses-chave: interpola rotações e pelve; os pés ficam plantados (controles em repouso)."""
    bones = armature.pose.bones
    keys = sorted(keys, key=lambda k: k["t"])
    after = next((i for i, k in enumerate(keys) if k["t"] >= t), len(keys) - 1)
    before = max(after - 1, 0)
    a, b = keys[before], keys[after]
    u = 0.0 if b["t"] == a["t"] else _smooth((t - a["t"]) / (b["t"] - a["t"]))
    names = set(a["bones"]) | set(b["bones"])
    for name in names:
        ra = a["bones"].get(name, (0, 0, 0))
        rb = b["bones"].get(name, (0, 0, 0))
        rig_utils.rotation_in_armature_axes(bones[name], tuple(x + (y - x) * u for x, y in zip(ra, rb)))
    pa, pb = a.get("pelvis", (0, 0, 0)), b.get("pelvis", (0, 0, 0))
    pelvis = bones["pelvis"]
    pelvis.location = _armature_delta(pelvis, tuple(x + (y - x) * u for x, y in zip(pa, pb)))


def apply_pose(armature, clip, t, right_arm_factor):
    bones = armature.pose.bones
    if clip.get("keys"):
        return apply_keys(armature, clip["keys"], t)
    gait = clip["gait"]
    cycle = 2 * math.pi * t
    moving = gait["stride_m"] > 0

    for side, offset in (("l", 0.0), ("r", 0.5)):
        y, lift, pitch = _foot_pose((t + offset) % 1.0, gait)
        control = bones[f"ctrl_foot_{side}"]
        control.location = (0, y, lift + _sole_clearance(pitch))
        rig_utils.rotation_in_armature_axes(control, (pitch, 0, 0))

    pelvis = bones["pelvis"]
    drop = gait["pelvis_drop_m"] + gait["pelvis_bob_m"] * math.cos(2 * cycle)
    if moving:
        sway = -0.012 * math.sin(cycle)
        pelvis.location = _armature_delta(pelvis, (sway, 0, -drop))
    else:
        pelvis.location = _armature_delta(pelvis, (0, 0, -drop))

    twist = gait.get("torso_twist_deg", 0.0)
    lean = gait.get("torso_lean_deg", 0.0)
    rig_utils.rotation_in_armature_axes(pelvis, (0, 0, twist * math.cos(cycle)))
    rig_utils.rotation_in_armature_axes(bones["spine_01"], (-lean, 0, 0))
    rig_utils.rotation_in_armature_axes(bones["chest"], (0, 0, -2 * twist * math.cos(cycle)))
    rig_utils.rotation_in_armature_axes(bones["head"], (lean * .8, 0, twist * math.cos(cycle)))

    swing = gait["arm_swing_deg"]
    bend = gait["forearm_bend_deg"]
    if moving:
        left, right = -swing * math.cos(cycle), swing * math.cos(cycle)
    else:
        left = swing * math.sin(cycle)
        right = swing * math.sin(cycle + 1.0)
        rig_utils.rotation_in_armature_axes(bones["chest"], (1.5 * math.sin(cycle), 0, 0))
        rig_utils.rotation_in_armature_axes(bones["head"], (-1.2 * math.sin(cycle), 0, 0))
    # A mão que segura a arma balança menos; a outra usa o balanço cheio.
    swing_by_side = {"l": left, "r": right}
    for side in "lr":
        factor = right_arm_factor if side == WEAPON_SIDE else 1.0
        rig_utils.rotation_in_armature_axes(bones[f"upper_arm_{side}"], (swing_by_side[side] * factor, 0, 0))
        # Cajado/arma: o antebraço compensa o balanço e a arma fica quase de pé.
        forearm = 6.0 - .7 * swing_by_side[side] * factor if side == WEAPON_SIDE else bend
        rig_utils.rotation_in_armature_axes(bones[f"forearm_{side}"], (forearm, 0, 0))


def _armature_delta(pose_bone, delta):
    """Delta em eixos canônicos → espaço local do osso de pose (sem pai rotacionado)."""
    from mathutils import Vector

    return pose_bone.bone.matrix_local.to_3x3().inverted() @ Vector(delta)


ANIMATED = [
    "ctrl_foot_l", "ctrl_foot_r", "pelvis", "spine_01", "chest", "neck", "head",
    "upper_arm_l", "upper_arm_r", "forearm_l", "forearm_r", "hand_l", "hand_r",
]


def bake_clip(armature, clip, right_arm_factor):
    scene = bpy.context.scene
    frames = clip["frame_count"]
    action = bpy.data.actions.new(f"clip_{clip['animation_id']}")
    action.use_fake_user = True
    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = action
    scene.render.fps = clip["fps"]
    for frame in range(frames + 1):
        rig_utils.reset_pose(armature)
        # Laço e ação que volta a outro estado: t ∈ [0, 1); o próximo quadro (pose neutra) é o do
        # estado seguinte, então nenhum quadro repete o primeiro. Ação terminal (morte): t vai até 1.
        terminal = not clip.get("loop", True) and clip.get("return_to") is None
        t = min(frame, frames - 1) / max(frames - 1, 1) if terminal else (frame % frames) / frames
        apply_pose(armature, clip, t, right_arm_factor)
        for name in ANIMATED:
            bone = armature.pose.bones[name]
            bone.keyframe_insert("rotation_quaternion", frame=frame)
            if name.startswith("ctrl_foot") or name == "pelvis":
                bone.keyframe_insert("location", frame=frame)
    return action


def use_action(armature, name):
    action = bpy.data.actions[name]
    armature.animation_data.action = action
    if armature.animation_data.action_slot is None and len(action.slots):
        armature.animation_data.action_slot = action.slots[0]
    return action
