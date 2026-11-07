"""Coleta fatos do rig; quem julga é o backend (engines/rig_engine).

Separa medição de veredito: nada aqui decide PASS/FAIL.
"""

import math

import bpy
from mathutils import Vector

from . import materials as mats
from . import rig as rig_utils
from . import scene as scene_utils

MARKERS = {
    "hand_l": (0.0, 1.0, 0.0),  # verde: punho esquerdo
    "hand_r": (0.0, 0.0, 1.0),  # azul: punho direito
    "foot_l": (1.0, 0.0, 1.0),  # magenta: tornozelo esquerdo
    "foot_r": (1.0, 1.0, 0.0),  # amarelo: tornozelo direito
    "qa_front": (0.0, 1.0, 1.0),  # ciano: frente
}


def _bones_report(armature):
    report = []
    for bone in armature.data.bones:
        report.append({
            "name": bone.name,
            "parent": bone.parent.name if bone.parent else None,
            "connected": bone.use_connect,
            "deform": bone.use_deform,
            "head": rig_utils.vec(bone.head_local),
            "tail": rig_utils.vec(bone.tail_local),
        })
    return report


def _skin_report(armature, rig):
    bone_names = {b.name for b in armature.data.bones}
    deform = {b.name for b in armature.data.bones if b.use_deform}
    left = {b["blender_name"] for b in rig["bones"] if b["side"] == "LEFT"}
    right = {b["blender_name"] for b in rig["bones"] if b["side"] == "RIGHT"}
    report = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not obj.name.isascii() or obj.name.startswith("QA_"):
            continue
        names = [g.name for g in obj.vertex_groups]
        no_influence = 0
        bad_sum = 0
        worst_sum = 0.0
        max_influences = 0
        crossed = 0
        for vertex in obj.data.vertices:
            weights = [(names[g.group], g.weight) for g in vertex.groups if g.weight > 0]
            max_influences = max(max_influences, len(weights))
            if not weights:
                no_influence += 1
                continue
            total = sum(w for _, w in weights)
            worst_sum = max(worst_sum, abs(total - 1.0))
            if abs(total - 1.0) > rig["weight_sum_tolerance"]:
                bad_sum += 1
            x = vertex.co.x
            for name, _ in weights:
                if (x < -0.02 and name in right) or (x > 0.02 and name in left):
                    crossed += 1
        report.append({
            "object": obj.name, "vertices": len(obj.data.vertices),
            "unknown_groups": sorted(set(names) - bone_names),
            "non_deform_groups": sorted(set(names) & (bone_names - deform)),
            "no_influence": no_influence, "bad_sum": bad_sum,
            "worst_sum_error": worst_sum, "max_influences": max_influences,
            "crossed_side": crossed,
        })
    return report


def _evaluated_vertices(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        points += [tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices]
        evaluated.to_mesh_clear()
    return points


def _sentinels(armature, rig):
    # O contorno (Solidify) desloca vértices por normal; a medição é da pele deformada.
    meshes = [bpy.data.objects["body"], bpy.data.objects["head"]]
    outlines = [m for obj in meshes for m in obj.modifiers if m.type == "SOLIDIFY"]
    for modifier in outlines:
        modifier.show_viewport = False
    watched = sorted({b["blender_name"] for b in rig["bones"]})
    rig_utils.reset_pose(armature)
    bpy.context.view_layer.update()
    rest_tails = {n: Vector(rig_utils.bone_world(armature, n, tail=True)) for n in watched}
    rest_verts = _evaluated_vertices(meshes)
    bind_x = [v.co.x for obj in meshes for v in obj.data.vertices]
    bind = [tuple(v.co) for obj in meshes for v in obj.data.vertices]
    bind_error = max((Vector(a) - Vector(b)).length for a, b in zip(bind, rest_verts))
    results = []
    for sentinel in rig["sentinel_poses"]:
        rig_utils.reset_pose(armature)
        bone = armature.pose.bones[sentinel["bone"]]
        if sentinel["mode"] == "translate":
            bone.location = bone.bone.matrix_local.to_3x3().inverted() @ Vector(sentinel["vector"])
        else:
            rig_utils.rotation_in_armature_axes(bone, sentinel["vector"])
        bpy.context.view_layer.update()
        moved = {
            n: (Vector(rig_utils.bone_world(armature, n, tail=True)) - rest_tails[n]).length
            for n in watched
        }
        verts = _evaluated_vertices(meshes)
        moved_x = [
            bind_x[i]
            for i in range(len(verts))
            if (Vector(verts[i]) - Vector(rest_verts[i])).length > 1e-4
        ]
        finite = all(math.isfinite(c) for v in verts for c in v)
        results.append({
            "id": sentinel["id"], "bone": sentinel["bone"], "moved_m": moved,
            "mesh_moved_vertices": len(moved_x),
            "mesh_moved_x_range": [min(moved_x), max(moved_x)] if moved_x else None,
            "mesh_finite": finite,
        })
    for modifier in outlines:
        modifier.show_viewport = True
    rig_utils.reset_pose(armature)
    bpy.context.view_layer.update()
    return results, bind_error


def _render_markers(scene, armature, payload):
    """Só marcadores ligados a ossos por constraint, sem o corpo: centróides exatos."""
    character = bpy.data.collections["ICS_Character"]
    character.hide_render = True
    for name, color in MARKERS.items():
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=.022)
        marker = bpy.context.object
        marker.name = f"QA_{name}"
        marker.data.materials.append(mats.flat_material(f"QA_{name}", color))
        constraint = marker.constraints.new("COPY_LOCATION")
        constraint.target = armature
        constraint.subtarget = name
    outputs = {}
    armature.rotation_mode = "XYZ"
    for direction, heading in payload["headings"].items():
        armature.rotation_euler = (0, 0, -math.radians(heading))
        bpy.context.view_layer.update()
        path = f"{payload['output_dir']}/markers_{direction}.png"
        scene_utils.render_to(scene, path)
        outputs[direction] = path
    armature.rotation_euler = (0, 0, 0)
    character.hide_render = False
    for name in MARKERS:
        bpy.data.objects.remove(bpy.data.objects[f"QA_{name}"])
    return outputs


def _render_sentinel_sheet(scene, armature, rig, payload):
    """Vista S e E de cada pose sentinela para revisão humana."""
    outputs = {}
    armature.rotation_mode = "XYZ"
    for sentinel in rig["sentinel_poses"]:
        rig_utils.reset_pose(armature)
        bone = armature.pose.bones[sentinel["bone"]]
        if sentinel["mode"] == "translate":
            bone.location = bone.bone.matrix_local.to_3x3().inverted() @ Vector(sentinel["vector"])
        else:
            rig_utils.rotation_in_armature_axes(bone, sentinel["vector"])
        for direction, heading in (("S", 180.0), ("E", 90.0)):
            armature.rotation_euler = (0, 0, -math.radians(heading))
            bpy.context.view_layer.update()
            path = f"{payload['output_dir']}/sentinel_{sentinel['id']}_{direction}.png"
            scene_utils.render_to(scene, path)
            outputs[f"{sentinel['id']}_{direction}"] = path
    rig_utils.reset_pose(armature)
    armature.rotation_euler = (0, 0, 0)
    return outputs


def run(payload):
    scene = bpy.context.scene
    armature = bpy.data.objects["ICS_Rig"]
    rig = payload["rig"]
    scene_utils.configure_render(scene, payload["render"])
    armature.animation_data_clear()
    sentinels, bind_error = _sentinels(armature, rig)
    return {
        "bind_error_m": bind_error,
        "sentinels": sentinels,
        "bones": _bones_report(armature),
        "ik": {
            name: [c.type for c in armature.pose.bones[chain["tip"]].constraints]
            for name, chain in rig["ik_chains"].items()
        },
        "skin": _skin_report(armature, rig),
        "marker_renders": _render_markers(scene, armature, payload),
        "sentinel_renders": _render_sentinel_sheet(scene, armature, rig, payload),
    }
