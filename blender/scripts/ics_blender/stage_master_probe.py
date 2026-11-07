"""Sonda de risco autorizada: pintura simples por região sobre o mestre, sem UV nem textura final.

Não é etapa de produção. Responde só a uma pergunta: com cor e luz, o sprite se aproxima da
referência? A cor vai por vértice, na paleta medida na prancha.
"""

import math

import bpy
import numpy as np

from . import master_body as mb
from . import materials as mats
from . import scene as scene_utils
from .scene import hex_to_linear

SKIN = "#B8693A"
HAIR = "#2B1A14"
RED = "#B5301F"
ORANGE = "#D9791F"
CREAM = "#E6CF9E"
LEATHER = "#5C3620"
DARK = "#1E120C"
BRASS = "#B98A3A"
TEAL = "#3F6A68"
WHITE = "#E8DFC8"

FLAT = {
    "belt": LEATHER, "waist_cloth": CREAM, "belt_rope": LEATHER, "belt_disc": BRASS,
    "loin_cream_front": CREAM, "loin_back": CREAM, "arm_band": LEATHER, "bracer": LEATHER,
    "knee_cuff": LEATHER, "shin_wrap": CREAM, "sandal_sole": DARK, "sandal_straps": LEATHER,
    "necklace_teeth": CREAM, "mouth_b": SKIN,
}


def linear(value):
    return np.array(hex_to_linear(value))


def body_colors(co):
    colors = np.tile(linear(SKIN), (len(co), 1))
    front = co[:, 1] > .06
    x, z = np.abs(co[:, 0]), co[:, 2]
    # Faixa vermelha do rosto, abaixo dos olhos, e risco na bochecha.
    colors[front & (np.abs(z - 1.056) < .013) & (x < .15)] = linear(RED)
    cheek = front & (co[:, 0] > .03) & (np.abs((z - 1.0) - (co[:, 0] - .06) * 1.1) < .011) & (z < 1.05)
    colors[cheek] = linear(RED)
    # Olhos: branco, íris e pálpebra superior pesada; sobrancelha inclinada.
    white = front & (((x - .062) / .034) ** 2 + ((z - 1.083) / .017) ** 2 < 1)
    colors[white] = linear(WHITE)
    iris = front & (((x - .058) / .015) ** 2 + ((z - 1.083) / .017) ** 2 < 1)
    colors[iris] = linear(DARK)
    lid = front & (np.abs(z - 1.1) < .0045) & (x > .026) & (x < .1)
    colors[lid] = linear(DARK)
    brow = front & (np.abs(z - (1.122 - (x - .03) * -.28 - .018)) < .0095) & (x > .022) & (x < .112)
    colors[brow] = linear(DARK)
    return colors


def hair_colors(co):
    colors = np.tile(linear(HAIR), (len(co), 1))
    crown = co[:, 2] > 1.31
    angle = np.arctan2(co[:, 0], co[:, 1] + .13)
    sector = ((angle + math.pi) / (2 * math.pi) * 6).astype(int) % 3
    palette = np.array([linear(RED), linear(CREAM), linear(ORANGE)])
    colors[crown & (co[:, 1] > -.3)] = palette[sector][crown & (co[:, 1] > -.3)]
    return colors


def tabard_colors(co):
    colors = np.tile(linear(RED), (len(co), 1))
    trim = (co[:, 2] < .3) | (np.abs(co[:, 0]) > .043)
    colors[trim] = linear(CREAM)
    inner = (np.abs(np.abs(co[:, 0]) - .024) < .004) & (co[:, 2] > .33) & (co[:, 2] < .5)
    colors[inner] = linear(CREAM)
    return colors


def feather_colors(co):
    colors = np.tile(linear(RED), (len(co), 1))
    tip = np.abs(co[:, 0]) > .3
    colors[tip] = linear(ORANGE)
    return colors


def beads_colors(co):
    colors = np.tile(linear(LEATHER), (len(co), 1))
    colors[np.abs(np.sin(co[:, 0] * 90)) > .6] = linear(TEAL)
    return colors


def object_colors(name, co):
    if name == "master_body":
        return body_colors(co)
    if name == "hair_b":
        return hair_colors(co)
    if name == "loin_red_tabard":
        return tabard_colors(co)
    if name == "shoulder_feathers":
        return feather_colors(co)
    if name == "necklace_beads":
        return beads_colors(co)
    for key, value in FLAT.items():
        if name.startswith(key):
            return np.tile(linear(value), (len(co), 1))
    return np.tile(linear(SKIN), (len(co), 1))


def painted_material(art):
    material = bpy.data.materials.new("ICS_paint")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.inputs["Color"].default_value = (1, 1, 1, 1)
    to_rgb = nodes.new("ShaderNodeShaderToRGB")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    elements = ramp.color_ramp.elements
    steps = art["toon_steps"]
    while len(elements) < len(steps):
        elements.new(.99)
    for element, (position, value) in zip(elements, steps):
        element.position = position
        element.color = (value, value, value, 1)
    attribute = nodes.new("ShaderNodeVertexColor")
    attribute.layer_name = "Col"
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1.0
    emission = nodes.new("ShaderNodeEmission")
    links.new(diffuse.outputs[0], to_rgb.inputs[0])
    links.new(to_rgb.outputs["Color"], ramp.inputs["Fac"])
    links.new(attribute.outputs["Color"], multiply.inputs[1])
    links.new(ramp.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs[0], emission.inputs["Color"])
    links.new(emission.outputs[0], output.inputs["Surface"])
    return material


def run(payload):
    scene = bpy.context.scene
    art = payload["art"]
    root = bpy.data.collections["MASTER"]
    meshes = [o for o in root.objects if o.type == "MESH"]
    material = painted_material(art)
    outline = mats.flat_material("ICS_paint_outline", tuple(c * .35 for c in hex_to_linear(DARK)))
    outline.use_backface_culling = True
    for obj in meshes:
        co = mb.read_co(obj.data)
        colors = object_colors(obj.name, co)
        attribute = obj.data.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
        rgba = np.column_stack((colors, np.ones(len(colors))))
        attribute.data.foreach_set("color", rgba.ravel())
        obj.data.materials.clear()
        obj.data.materials.append(material)
        obj.data.materials.append(outline)
        if obj.name != "mouth_b":
            solidify = obj.modifiers.new("outline", "SOLIDIFY")
            solidify.thickness = art["outline_thickness_m"]
            solidify.offset = 1.0
            solidify.use_flip_normals = True
            solidify.use_rim = False
            solidify.material_offset = 1
    pivot = bpy.data.objects.new("paint_pivot", None)
    scene.collection.objects.link(pivot)
    for obj in root.objects:
        if obj.parent is None:
            obj.parent = pivot
    if scene.world is None or not payload.get("reuse_lights"):
        scene_utils.add_lights(scene, art)
    pivot.rotation_mode = "XYZ"
    outputs = {}
    for shot in payload["shots"]:
        scene_utils.configure_render(scene, shot["render"])
        if scene.camera is not None:
            bpy.data.objects.remove(scene.camera)
        scene_utils.add_camera(scene, shot["render"])
        pivot.rotation_euler = (0, 0, -math.radians(shot["heading"]))
        bpy.context.view_layer.update()
        path = f"{payload['output_dir']}/{shot['name']}.png"
        scene_utils.render_to(scene, path)
        outputs[shot["name"]] = path
    return {"outputs": outputs}
