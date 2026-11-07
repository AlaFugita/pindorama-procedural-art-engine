"""Configuração determinística de cena, câmera, luz e saída de render."""

import math

import bpy
from mathutils import Matrix, Vector


def hex_to_linear(value):
    """#RRGGBB sRGB → RGB linear (Blender trabalha em linear)."""

    def channel(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    text = value.lstrip("#")
    return tuple(channel(int(text[i : i + 2], 16)) for i in (0, 2, 4))


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def configure_render(scene, render):
    """Aplica RenderProfile. ``media_type`` precede ``file_format`` desde o Blender 5.0."""
    scene.render.engine = render["engine"]
    scene.render.resolution_x = render["canvas"]["width"]
    scene.render.resolution_y = render["canvas"]["height"]
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.filter_size = render.get("filter_width_px", 1.5)
    scene.render.use_compositing = False
    scene.render.use_sequencer = False
    settings = scene.render.image_settings
    settings.media_type = "IMAGE"
    settings.file_format = "PNG"
    settings.color_mode = "RGBA"
    settings.color_depth = "8"
    settings.compression = 15
    scene.view_settings.view_transform = render.get("view_transform", "Standard")
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.display_settings.display_device = "sRGB"
    scene.eevee.taa_render_samples = render["samples"]


def add_camera(scene, render):
    data = bpy.data.cameras.new("ICS_Camera")
    data.type = "ORTHO"
    data.ortho_scale = render["camera"]["ortho_scale"]
    data.sensor_fit = "AUTO"
    data.clip_start = 0.1
    data.clip_end = 100.0
    camera = bpy.data.objects.new("ICS_Camera", data)
    scene.collection.objects.link(camera)
    camera.matrix_world = Matrix(render["camera"]["matrix_world"])
    scene.camera = camera
    return camera


def add_lights(scene, art):
    if scene.world is None:
        scene.world = bpy.data.worlds.new("ICS_World")
    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background") or next(
        n for n in world.node_tree.nodes if n.type == "BACKGROUND"
    )
    background.inputs[0].default_value = (*hex_to_linear(art["world_color"]), 1.0)
    background.inputs[1].default_value = art["world_strength"]
    for light in art["lights"]:
        data = bpy.data.lights.new(f"ICS_{light['name']}", "SUN")
        data.energy = light["energy"]
        data.color = hex_to_linear(light["color"])
        data.angle = math.radians(light["angle_deg"])
        data.use_shadow = art.get("light_shadows", True)
        obj = bpy.data.objects.new(f"ICS_{light['name']}", data)
        scene.collection.objects.link(obj)
        azimuth = math.radians(light["azimuth_deg"])
        elevation = math.radians(light["elevation_deg"])
        to_light = Vector(
            (
                math.sin(azimuth) * math.cos(elevation),
                math.cos(azimuth) * math.cos(elevation),
                math.sin(elevation),
            )
        )
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = to_light.to_track_quat("Z", "Y")


def render_to(scene, path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
