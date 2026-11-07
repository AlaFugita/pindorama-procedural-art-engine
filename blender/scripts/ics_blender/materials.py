"""Materiais toon do perfil artístico: difuso → faixas → cor base; contorno por casca invertida."""

import bpy

from .scene import hex_to_linear


def toon_material(name, hex_color, art):
    material = bpy.data.materials.new(name)
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
        elements.new(0.99)
    for element, (position, value) in zip(elements, steps):
        element.position = position
        element.color = (value, value, value, 1)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1.0
    multiply.inputs[1].default_value = (*hex_to_linear(hex_color), 1)
    emission = nodes.new("ShaderNodeEmission")
    links.new(diffuse.outputs[0], to_rgb.inputs[0])
    links.new(to_rgb.outputs["Color"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs[0], emission.inputs["Color"])
    links.new(emission.outputs[0], output.inputs["Surface"])
    return material


def flat_material(name, rgb_linear):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*rgb_linear, 1)
    material.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    return material


def outline_material(name, hex_color, art):
    linear = hex_to_linear(hex_color)
    material = flat_material(name, tuple(c * art["outline_darken"] for c in linear))
    material.use_backface_culling = True
    return material


def resolve_color(key, palette):
    if key.startswith("#"):
        return key
    return palette[key]
