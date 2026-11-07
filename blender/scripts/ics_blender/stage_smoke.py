"""Fase 0: cena determinística de teste → um PNG RGBA + dados da cena."""

import bpy

from . import scene as scene_utils


def run(payload):
    scene = scene_utils.clear_scene()
    scene_utils.configure_render(scene, payload["render"])
    camera = scene_utils.add_camera(scene, payload["render"])
    scene_utils.add_lights(scene, payload["art"])

    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, 0, 0.3))
    cube = bpy.context.object
    material = bpy.data.materials.new("smoke")
    material.diffuse_color = (0.6, 0.2, 0.1, 1)
    cube.data.materials.append(material)

    scene_utils.render_to(scene, payload["output_png"])
    return {
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "camera_type": camera.data.type,
        "ortho_scale": camera.data.ortho_scale,
        "output_png": payload["output_png"],
    }
