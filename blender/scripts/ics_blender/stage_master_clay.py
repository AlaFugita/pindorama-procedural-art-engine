"""Estúdio de argila idêntico para qualquer rota: mesma câmera, luz e material neutro.

Sem textura, por regra (D-MASTER-2): a forma não pode se esconder atrás de pintura. Workbench é
determinístico e não depende de luzes da cena. Cada vista gera também a silhueta em preto.
"""

import math

import bpy
from mathutils import Matrix, Vector


def _bounds(objects):
    points = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    return [min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]


def _camera(scene, heading, elevation, target, ortho):
    azimuth = math.radians(heading)
    e = math.radians(elevation)
    # heading = para onde o personagem olha, relativo à câmera ao sul; 180 mostra a frente.
    forward = Vector((0, math.cos(e), -math.sin(e)))
    right = Vector((1, 0, 0))
    up = right.cross(forward)
    camera = scene.camera
    camera.data.ortho_scale = ortho
    matrix = Matrix.Identity(4)
    for row in range(3):
        matrix[row][0], matrix[row][1], matrix[row][2] = right[row], up[row], -forward[row]
    matrix.translation = Vector(target) - forward * 20
    camera.matrix_world = matrix
    return azimuth


def run(payload):
    scene = bpy.context.scene
    root = bpy.data.collections.get("MASTER")
    objects = [o for o in root.objects if o.type == "MESH"]
    pivot = bpy.data.objects.new("MASTER_pivot", None)
    scene.collection.objects.link(pivot)
    for obj in root.objects:
        if obj.parent is None:
            obj.parent = pivot
    data = bpy.data.cameras.new("clay")
    data.type = "ORTHO"
    camera = bpy.data.objects.new("clay", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    painted = payload.get("painted", False)
    scene.render.engine = "BLENDER_EEVEE" if painted else "BLENDER_WORKBENCH"
    if painted:
        scene.view_settings.view_transform = "Standard"
        scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = payload["width"]
    scene.render.resolution_y = payload["height"]
    scene.render.film_transparent = True
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filter_size = 1.2
    scene.display.render_aa = "32"
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.studio_light = payload.get("studio_light", "paint.sl")
    shading.color_type = "SINGLE"
    shading.single_color = (.72, .68, .64)
    shading.show_cavity = True
    shading.cavity_type = "BOTH"
    shading.cavity_ridge_factor = 1.0
    shading.cavity_valley_factor = 1.2
    shading.curvature_ridge_factor = .7
    shading.curvature_valley_factor = .9
    shading.show_shadows = False  # sombra dura mancha a forma e confunde a leitura da argila

    bpy.context.view_layer.update()
    minimum, maximum = _bounds(objects)
    height = maximum[2] - minimum[2]
    ortho = payload.get("ortho", height * 1.12)
    target = (0, 0, minimum[2] + height / 2)

    outputs = {}
    for view in payload["views"]:
        pivot.rotation_euler = (0, 0, -math.radians(view["heading"]))
        focus = (0, 0, view["focus_z"]) if "focus_z" in view else target
        _camera(scene, view["heading"], view["elevation"], focus, view.get("ortho", ortho))
        bpy.context.view_layer.update()
        scene.render.filepath = f"{payload['output_dir']}/{view['name']}.png"
        bpy.ops.render.render(write_still=True)
        outputs[view["name"]] = scene.render.filepath
    return {
        "views": outputs,
        "bounds": [minimum, maximum],
        "height_m": height,
        "faces": sum(len(o.data.polygons) for o in objects),
        "vertices": sum(len(o.data.vertices) for o in objects),
    }
