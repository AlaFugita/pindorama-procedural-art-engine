"""Armature a partir do RigProfile, IK de pernas e pesos determinísticos.

Os pesos não usam o Bone Heat do Blender: são calculados pela distância aos segmentos dos
ossos, com filtro de lado. Assim a esquerda nunca recebe influência direita, por construção
e por validação, e o resultado é reprodutível.
"""

import math

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector


def build_armature(scene, rig):
    data = bpy.data.armatures.new("ICS_Rig")
    armature = bpy.data.objects.new("ICS_Rig", data)
    scene.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    edit = data.edit_bones
    for spec in rig["bones"]:
        bone = edit.new(spec["blender_name"])
        bone.head = spec["head"]
        bone.tail = spec["tail"]
        bone.roll = math.radians(spec["roll_deg"])
        bone.use_deform = spec["deform"]
    for spec in rig["bones"]:
        if spec["parent"]:
            bone = edit[spec["blender_name"]]
            bone.parent = edit[spec["parent"]]
            bone.use_connect = spec["connected"]
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature


def _pole_angle(armature, chain):
    """Ângulo de pole que preserva a pose de repouso (joelho sem torção)."""
    base = armature.pose.bones[chain["base"]]
    tip = armature.pose.bones[chain["tip"]]
    pole = armature.pose.bones[chain["pole"]]
    head = base.bone.head_local
    normal = (tip.bone.tail_local - head).cross(pole.bone.head_local - head)
    x_axis = _axis(base, 0)
    y_axis = _axis(base, 1)
    projected = normal.cross(y_axis)
    if x_axis.cross(projected).length < 1e-9:
        return 0.0
    angle = x_axis.angle(projected)
    return -angle if x_axis.cross(projected).dot(y_axis) > 0 else angle


def _axis(pose_bone, index):
    return pose_bone.bone.matrix_local.to_3x3().col[index].normalized()


def setup_ik(armature, rig):
    for chain in rig["ik_chains"].values():
        tip = armature.pose.bones[chain["tip"]]
        ik = tip.constraints.new("IK")
        ik.name = "ICS_IK"
        ik.target = armature
        ik.subtarget = chain["target"]
        ik.pole_target = armature
        ik.pole_subtarget = chain["pole"]
        ik.chain_count = 2
        ik.use_stretch = False
        ik.pole_angle = _pole_angle(armature, chain)
        foot = armature.pose.bones[chain["foot"]]
        copy = foot.constraints.new("COPY_ROTATION")
        copy.name = "ICS_FootRot"
        copy.target = armature
        copy.subtarget = chain["target"]
        copy.target_space = "WORLD"
        copy.owner_space = "WORLD"
    for pose_bone in armature.pose.bones:
        pose_bone.rotation_mode = "QUATERNION"


def reset_pose(armature):
    for pose_bone in armature.pose.bones:
        pose_bone.location = (0, 0, 0)
        pose_bone.rotation_quaternion = (1, 0, 0, 0)
        pose_bone.scale = (1, 1, 1)


def rotation_in_armature_axes(pose_bone, degrees_xyz):
    """Rotação expressa nos eixos canônicos da pose de repouso, em torno da cabeça do osso."""
    rest = pose_bone.bone.matrix_local.to_quaternion()
    result = Quaternion()
    for axis, degrees in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), degrees_xyz):
        if degrees:
            result = Quaternion(axis, math.radians(degrees)) @ result
    pose_bone.rotation_quaternion = rest.inverted() @ result @ rest


def segments(armature, names):
    data = armature.data.bones
    return (
        np.array([tuple(data[n].head_local) for n in names]),
        np.array([tuple(data[n].tail_local) for n in names]),
    )


def _distances(points, heads, tails):
    edges = tails - heads
    lengths = np.maximum((edges * edges).sum(axis=1), 1e-12)
    offset = points[:, None, :] - heads[None, :, :]
    t = np.clip((offset * edges[None]).sum(axis=2) / lengths, 0, 1)
    closest = heads[None] + t[..., None] * edges[None]
    return np.linalg.norm(points[:, None, :] - closest, axis=2)


def _vertex_array(mesh):
    points = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get("co", points)
    return points.reshape(-1, 3)


SIDE_BAND_M = 0.015


def skin_weights(obj, armature, skin, rig, power=8.0):
    """Cria grupos de vértices. ``skin`` = {"rigid": osso} ou {"bones": [...], "exclude": [...]}."""
    mesh = obj.data
    influences = rig["max_influences"]
    if "rigid" in skin:
        group = obj.vertex_groups.new(name=skin["rigid"])
        group.add(list(range(len(mesh.vertices))), 1.0, "REPLACE")
    else:
        names = [n for n in skin["bones"] if n not in skin.get("exclude", ())]
        side = {b["blender_name"]: b["side"] for b in rig["bones"]}
        points = _vertex_array(mesh)
        heads, tails = segments(armature, names)
        dist = _distances(points, heads, tails) + 1e-4
        weights = dist ** -power
        left = np.array([side[n] == "LEFT" for n in names])
        right = np.array([side[n] == "RIGHT" for n in names])
        weights[np.ix_(points[:, 0] < -SIDE_BAND_M, right)] = 0
        weights[np.ix_(points[:, 0] > SIDE_BAND_M, left)] = 0
        order = np.argsort(-weights, axis=1)
        keep = order[:, :influences]
        mask = np.zeros_like(weights, dtype=bool)
        np.put_along_axis(mask, keep, True, axis=1)
        weights = np.where(mask, weights, 0)
        weights /= weights.sum(axis=1, keepdims=True)
        for index, name in enumerate(names):
            column = weights[:, index]
            verts = np.flatnonzero(column > 1e-4)
            if len(verts) == 0:
                continue
            group = obj.vertex_groups.new(name=name)
            for vertex in verts.tolist():
                group.add([vertex], float(column[vertex]), "REPLACE")
        _renormalize(obj)
    modifier = obj.modifiers.new("ICS_Armature", "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    obj.parent = armature
    obj.matrix_parent_inverse = Matrix.Identity(4)


def _renormalize(obj):
    """Pequenos pesos descartados não podem deixar a soma ≠ 1."""
    groups = obj.vertex_groups
    for vertex in obj.data.vertices:
        total = sum(g.weight for g in vertex.groups)
        if total <= 0:
            raise RuntimeError(f"{obj.name}: vértice {vertex.index} sem influência")
        for g in vertex.groups:
            g.weight = g.weight / total
    return groups


def bone_world(armature, name, tail=False):
    pose_bone = armature.pose.bones[name]
    return armature.matrix_world @ (pose_bone.tail if tail else pose_bone.head)


def vec(value):
    return [float(c) for c in value]


__all__ = ["Vector", "build_armature", "setup_ik", "skin_weights", "reset_pose"]
