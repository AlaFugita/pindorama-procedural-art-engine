"""Prova funcional do mestre: rig de teste, pose extrema e medição de deformação.

Não produz animação (regra 1). Só responde se a malha aceita um esqueleto e como ela reage.
"""

import bpy
import numpy as np
from mathutils import Vector

from . import master_body as mb
from . import rig as rig_utils


A_JOINTS = {
    "pelvis": .47, "waist": .585, "ribs": .70, "neck": .875, "chin": .929, "top": 1.30,
    "clav": (.05, .84), "shoulder": (.215, .805), "elbow": (.305, .575), "wrist": (.355, .395),
    "fingers": (.378, .225), "hip": (.10, .47), "knee": (.105, .27), "ankle": (.11, .08),
    "toe": (.128, .205, .018),
}


def _bones(j):
    def bone(name, parent, head, tail, side="CENTER", connected=False):
        return {"blender_name": name, "parent": parent, "head": head, "tail": tail, "side": side,
                "deform": True, "roll_deg": 0.0, "connected": connected}

    bones = [
        bone("pelvis", None, (0, 0, j["pelvis"]), (0, 0, j["waist"])),
        bone("spine_01", "pelvis", (0, 0, j["waist"]), (0, 0, j["ribs"]), connected=True),
        bone("chest", "spine_01", (0, 0, j["ribs"]), (0, .01, j["neck"]), connected=True),
        bone("neck", "chest", (0, .01, j["neck"]), (0, 0, j["chin"]), connected=True),
        bone("head", "neck", (0, 0, j["chin"]), (0, 0, j["top"]), connected=True),
    ]
    for suffix, sign, side in (("l", -1, "LEFT"), ("r", 1, "RIGHT")):
        s = suffix
        chain = [
            (f"clavicle_{s}", "chest", (j["clav"][0], 0, j["clav"][1]), (j["shoulder"][0], 0, j["shoulder"][1]), False),
            (f"upper_arm_{s}", f"clavicle_{s}", (j["shoulder"][0], 0, j["shoulder"][1]), (j["elbow"][0], 0, j["elbow"][1]), True),
            (f"forearm_{s}", f"upper_arm_{s}", (j["elbow"][0], 0, j["elbow"][1]), (j["wrist"][0], .012, j["wrist"][1]), True),
            (f"hand_{s}", f"forearm_{s}", (j["wrist"][0], .012, j["wrist"][1]), (j["fingers"][0], .02, j["fingers"][1]), True),
            (f"thigh_{s}", "pelvis", (j["hip"][0], 0, j["hip"][1]), (j["knee"][0], .012, j["knee"][1]), False),
            (f"shin_{s}", f"thigh_{s}", (j["knee"][0], .012, j["knee"][1]), (j["ankle"][0], 0, j["ankle"][1]), True),
            (f"foot_{s}", f"shin_{s}", (j["ankle"][0], 0, j["ankle"][1]), j["toe"], True),
        ]
        for name, parent, head, tail, connected in chain:
            flip = (sign, 1, 1)
            bones.append(bone(name, parent, tuple(a * b for a, b in zip(head, flip)),
                              tuple(a * b for a, b in zip(tail, flip)), side, connected))
    return bones


def _skin_rule(name):
    arm = ["clavicle", "upper_arm", "forearm", "hand"]
    leg = ["thigh", "shin", "foot"]
    both = lambda groups: [f"{g}_{s}" for g in groups for s in "lr"]  # noqa: E731
    if name.startswith(("hair", "crown", "earrings", "GEO-body", "mouth_b")):
        return {"rigid": "head"}
    if name.startswith(("belt", "waist", "loin")):
        return {"bones": ["pelvis", "spine_01", "thigh_l", "thigh_r"]}
    if name.startswith("necklace"):
        return {"rigid": "chest"}
    if name.startswith("fist_"):
        return {"rigid": f"hand_{name[-1]}"}
    if name.startswith("shoulder"):
        return {"bones": ["chest", "clavicle_l", "clavicle_r", "upper_arm_l", "upper_arm_r"]}
    if name.startswith(("arm_band", "bracer")):
        return {"bones": both(arm)}
    return {"bones": both(leg)}


def _world_edges(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        co = mb.read_co(mesh)
        edges = mb.edge_array(mesh)
        result.append(np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1))
        evaluated.to_mesh_clear()
    return np.concatenate(result)


def run(payload):
    scene = bpy.context.scene
    root = bpy.data.collections["MASTER"]
    meshes = [o for o in root.objects if o.type == "MESH"]
    if payload.get("decimate"):
        body = bpy.data.objects["master_body"]
        modifier = body.modifiers.new("decimate", "DECIMATE")
        modifier.ratio = payload["decimate"]
        depsgraph = bpy.context.evaluated_depsgraph_get()
        reduced = bpy.data.meshes.new_from_object(body.evaluated_get(depsgraph))
        body.modifiers.clear()
        body.data = reduced
    bones = _bones(payload.get("joints", A_JOINTS))
    rig = {"bones": bones, "max_influences": 4}
    armature = rig_utils.build_armature(scene, rig)
    for pose_bone in armature.pose.bones:
        pose_bone.rotation_mode = "QUATERNION"
    deform = [b["blender_name"] for b in bones]
    for obj in meshes:
        exclude = payload.get("body_exclude", ["head"])
        rule = {"bones": deform, "exclude": exclude} if obj.name == "master_body" else _skin_rule(obj.name)
        rig_utils.skin_weights(obj, armature, rule, rig)
    root.objects.link(armature)
    scene.collection.objects.unlink(armature)
    bpy.context.view_layer.update()
    rest_edges = _world_edges(meshes)
    bones_p = armature.pose.bones
    for name, degrees in payload["pose"].items():
        rig_utils.rotation_in_armature_axes(bones_p[name], degrees)
    bpy.context.view_layer.update()
    posed_edges = _world_edges(meshes)
    finite = bool(np.isfinite(posed_edges).all())
    ratio = posed_edges / np.maximum(rest_edges, 1e-6)
    body = bpy.data.objects["master_body"]
    co = mb.read_co(body.data)
    chin_slice = co[(co[:, 1] > .1) & (co[:, 2] > .85) & (np.abs(co[:, 0]) < .05)]
    chin = float(chin_slice[:, 2].min()) if len(chin_slice) else -1.0
    top = float(co[:, 2].max())
    bottom = float(co[:, 2].min())
    bpy.ops.wm.save_as_mainfile(filepath=payload["blend_path"], compress=True)
    return {
        "bones": len(bones), "finite": finite, "meshes_bound": len(meshes),
        "edge_stretch_p99": float(np.percentile(ratio, 99)),
        "edge_stretch_max": float(ratio.max()), "edge_compress_p1": float(np.percentile(ratio, 1)),
        "chin_z": chin, "head_top_z": top, "feet_z": bottom,
        "heads_measured": (top - bottom) / (top - chin),
        "armature_location": [float(c) for c in Vector(armature.location)],
    }
