"""Passes nativos para pixel art: identidade da peça, luz e profundidade, na grade final.

Para cada quadro renderiza:
- ``id``: emissão com o índice da peça (1 amostra, sem antialiasing, transformação Raw);
- ``light``: R = luz direcional com sombra projetada (Diffuse → Shader to RGB),
  G = oclusão ambiente, B = máscara de padrão do tecido;
- ``depth``: profundidade da câmera normalizada em 16 bits.
A casca de contorno 3D é desligada: o contorno é desenhado em 2D na composição.
"""

import json
import math
import os
import time

import bpy

from . import animation as anim
from . import scene as scene_utils

DEPTH_NEAR, DEPTH_FAR = 0.1, 40.0


def _emission_material(name, build):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    emission = tree.nodes.new("ShaderNodeEmission")
    tree.links.new(emission.outputs[0], out.inputs["Surface"])
    build(tree, emission)
    return material


def _id_material(index):
    def build(tree, emission):
        emission.inputs["Color"].default_value = (index / 255.0, 0, 0, 1)
    return _emission_material(f"PX_id_{index}", build)


def _pattern(tree, kind, scale):
    """Máscara 0/1 em coordenadas do objeto: o padrão gira junto com a peça."""
    coords = tree.nodes.new("ShaderNodeTexCoord")
    if kind == "stitch":
        tex = tree.nodes.new("ShaderNodeTexWave")
        tex.wave_type = "RINGS"
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Distortion"].default_value = 0
        socket = tex.outputs["Fac"]
        threshold = .82
    elif kind == "weave":
        tex = tree.nodes.new("ShaderNodeTexChecker")
        tex.inputs["Scale"].default_value = scale
        socket = tex.outputs["Fac"]
        threshold = .5
    elif kind == "grain":
        tex = tree.nodes.new("ShaderNodeTexWave")
        tex.wave_type = "BANDS"
        tex.bands_direction = "Z"
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Distortion"].default_value = 6
        socket = tex.outputs["Fac"]
        threshold = .78
    else:  # glyph
        tex = tree.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Mortar Size"].default_value = .12
        socket = tex.outputs["Fac"]
        threshold = .5
    tree.links.new(coords.outputs["Object"], tex.inputs["Vector"])
    step = tree.nodes.new("ShaderNodeMath")
    step.operation = "GREATER_THAN"
    step.inputs[1].default_value = threshold
    tree.links.new(socket, step.inputs[0])
    return step.outputs[0]


def _light_material(name, role):
    def build(tree, emission):
        diffuse = tree.nodes.new("ShaderNodeBsdfDiffuse")
        diffuse.inputs["Color"].default_value = (1, 1, 1, 1)
        to_rgb = tree.nodes.new("ShaderNodeShaderToRGB")
        tree.links.new(diffuse.outputs[0], to_rgb.inputs[0])
        ao = tree.nodes.new("ShaderNodeAmbientOcclusion")
        ao.inputs["Distance"].default_value = .1
        combine = tree.nodes.new("ShaderNodeCombineColor")
        bw = tree.nodes.new("ShaderNodeRGBToBW")
        tree.links.new(to_rgb.outputs["Color"], bw.inputs[0])
        scale = tree.nodes.new("ShaderNodeMath")
        scale.operation = "MULTIPLY"
        scale.inputs[1].default_value = .5  # luz até 2.0 cabe em 0..1
        tree.links.new(bw.outputs[0], scale.inputs[0])
        tree.links.new(scale.outputs[0], combine.inputs[0])
        tree.links.new(ao.outputs["AO"], combine.inputs[1])
        if role.get("pattern"):
            tree.links.new(_pattern(tree, role["pattern"], role.get("pattern_scale", 40.0)), combine.inputs[2])
        tree.links.new(combine.outputs[0], emission.inputs["Color"])
    return _emission_material(name, build)


def _depth_material():
    """R = profundidade normalizada; G = ruído de baixa frequência em coordenadas do objeto
    (textura contínua estável entre quadros, porque acompanha a peça)."""
    def build(tree, emission):
        camera = tree.nodes.new("ShaderNodeCameraData")
        remap = tree.nodes.new("ShaderNodeMapRange")
        remap.inputs["From Min"].default_value = DEPTH_NEAR
        remap.inputs["From Max"].default_value = DEPTH_FAR
        tree.links.new(camera.outputs["View Z Depth"], remap.inputs["Value"])
        coords = tree.nodes.new("ShaderNodeTexCoord")
        noise = tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 9.0
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = .55
        tree.links.new(coords.outputs["Object"], noise.inputs["Vector"])
        combine = tree.nodes.new("ShaderNodeCombineColor")
        tree.links.new(remap.outputs["Result"], combine.inputs[0])
        tree.links.new(noise.outputs["Fac"], combine.inputs[1])
        tree.links.new(combine.outputs[0], emission.inputs["Color"])
        emission.inputs["Strength"].default_value = 1.0
    return _emission_material("PX_depth", build)


def _set_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def run(payload):
    scene = bpy.context.scene
    armature = bpy.data.objects["ICS_Rig"]
    render = payload["render"]
    scene_utils.configure_render(scene, render)
    scene.view_settings.view_transform = "Raw"
    scene.render.filter_size = 0.0
    scene.render.image_settings.color_depth = "16"
    for light in bpy.data.lights:
        light.use_shadow = True
    parts = sorted((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: o.name)
    if len(parts) > 254:
        raise ValueError("mais de 254 peças: o índice não cabe em 8 bits")
    cfg = payload["pixel"]

    def role_of(name):
        table = cfg["part_roles"]
        if name in table:
            return cfg["roles"][table[name]]
        best = max((k for k in table if k != "*" and name.startswith(k)), key=len, default=None)
        return cfg["roles"][table[best] if best else table.get("*", "default")]

    depth_material = _depth_material()
    sets = {}
    meta = []
    for index, obj in enumerate(parts, start=1):
        for mod in obj.modifiers:
            if mod.type == "SOLIDIFY":
                mod.show_render = False
                mod.show_viewport = False
        role = role_of(obj.name)
        sets[obj.name] = {
            "id": _id_material(index),
            "light": _light_material(f"PX_light_{obj.name}", role),
            "depth": depth_material,
        }
        meta.append({"index": index, "name": obj.name, "color": obj.get("ics_color", "")})
    armature.rotation_mode = "XYZ"
    root = payload["output_dir"]
    samples = {"id": 1, "light": payload.get("light_samples", 16), "depth": 1}
    started = time.monotonic()
    done = 0
    for clip in payload["clips"]:
        anim.use_action(armature, f"clip_{clip['animation_id']}")
        for direction in render["direction_order"]:
            armature.rotation_euler = (0, 0, -math.radians(render["headings_deg"][direction]))
            folder = os.path.join(root, clip["animation_id"], direction)
            os.makedirs(folder, exist_ok=True)
            for frame in range(clip["frame_count"]):
                scene.frame_set(frame)
                for kind in ("id", "light", "depth"):
                    for obj in parts:
                        _set_material(obj, sets[obj.name][kind])
                    scene.eevee.taa_render_samples = samples[kind]
                    scene_utils.render_to(scene, os.path.join(folder, f"{frame:04d}_{kind}.png"))
                done += 1
    with open(os.path.join(root, "parts.json"), "w", encoding="utf-8") as stream:
        json.dump(meta, stream, indent=1)
    return {"parts": meta, "frames": done, "seconds": time.monotonic() - started,
            "depth_range_m": [DEPTH_NEAR, DEPTH_FAR]}
