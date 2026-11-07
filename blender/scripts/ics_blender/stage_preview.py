"""Render estático de inspeção em headings pedidos, com arquivo .blend já aberto."""

import math

import bpy

from . import scene as scene_utils


def run(payload):
    scene = bpy.context.scene
    armature = bpy.data.objects["ICS_Rig"]
    scene_utils.configure_render(scene, payload["render"])
    if armature.animation_data:
        armature.animation_data.action = None
    from . import rig as rig_utils

    rig_utils.reset_pose(armature)
    armature.rotation_mode = "XYZ"
    outputs = []
    for name, heading in payload["headings"].items():
        armature.rotation_euler = (0, 0, -math.radians(heading))
        bpy.context.view_layer.update()
        path = f"{payload['output_dir']}/{name}.png"
        scene_utils.render_to(scene, path)
        outputs.append(path)
    return {"outputs": outputs}
