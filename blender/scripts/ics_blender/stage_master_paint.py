"""Teste de direção de textura: pintura da referência projetada na B e levada à base aprovada.

A Rota B nasceu da própria imagem, então existe um ângulo em que suas vértices caem sobre a
pintura. Esse ângulo é encontrado por silhueta; cores vão à B e depois, por proximidade, à base.
Áreas sem visão recebem o espelho e, por fim, a cor visível mais próxima: o verso é estimado.
A projeção vale só na cabeça, onde a B coincide com a prancha; o resto usa cor por peça.
Local, sem IA e sem serviços externos. Não é a textura final: mostra a direção de arte.
"""

import math

import bpy
import numpy as np
from mathutils.kdtree import KDTree

from . import body_paint as bp
from . import materials as mats
from . import stage_master_c as sc
from .master_body import read_co


def _image_rgba(path):
    image = bpy.data.images.load(path)
    width, height = image.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    data = pixels.reshape(height, width, 4)[::-1].copy()  # origem no topo
    return data


def _rotate(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.column_stack((points[:, 0] * c - points[:, 1] * s, points[:, 0] * s + points[:, 1] * c, points[:, 2]))


def _project(points, phi, elevation, ref_box, size):
    """(x_img, y_img, profundidade) em pixels da imagem de referência."""
    rot = _rotate(points, phi)
    e = math.radians(elevation)
    depth = rot[:, 1] * math.cos(e) - rot[:, 2] * math.sin(e)
    up = rot[:, 1] * math.sin(e) + rot[:, 2] * math.cos(e)
    x0, y0, x1, y1 = ref_box
    scale = (y1 - y0) / (up.max() - up.min())
    px = rot[:, 0] * scale
    py = (up.max() - up) * scale + y0
    px = px - (px.min() + px.max()) / 2 + (x0 + x1) / 2
    return px, py, depth


def _silhouette(px, py, shape):
    canvas = np.zeros(shape, dtype=bool)
    ix = np.clip(px.astype(int), 1, shape[1] - 2)
    iy = np.clip(py.astype(int), 1, shape[0] - 2)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            canvas[iy + dy, ix + dx] = True
    return canvas


def fit_view(points, alpha, sector=(-180, 180)):
    mask = alpha > .5
    ys, xs = np.nonzero(mask)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    sample = points[:: max(len(points) // 60000, 1)]
    best = (-1.0, 0.0, 0.0)
    for elevation in (0, 8, 16):
        for degrees in range(sector[0], sector[1], 5):
            px, py, _ = _project(sample, math.radians(degrees), elevation, box, None)
            shot = _silhouette(px, py, mask.shape)
            score = (shot & mask).sum() / (shot | mask).sum()
            if score > best[0]:
                best = (float(score), float(degrees), float(elevation))
    print("MP ajuste IoU %.3f phi %.0f elev %.0f" % best)
    return best, box


def sample_colors(points, image, phi, elevation, box):
    px, py, depth = _project(points, phi, elevation, box, None)
    height, width = image.shape[:2]
    ix = np.clip(px.astype(int), 0, width - 1)
    iy = np.clip(py.astype(int), 0, height - 1)
    buffer = np.full((height // 2 + 1, width // 2 + 1), np.inf)
    np.minimum.at(buffer, (iy // 2, ix // 2), depth)
    visible = depth <= buffer[iy // 2, ix // 2] + .03
    visible &= image[iy, ix, 3] > .5
    colors = np.zeros((len(points), 3), dtype=np.float32)
    colors[visible] = image[iy[visible], ix[visible], :3]
    return colors, visible


def fill_unseen(points, colors, visible):
    tree = KDTree(int(visible.sum()))
    indices = np.flatnonzero(visible)
    for slot, index in enumerate(indices.tolist()):
        tree.insert(points[index], slot)
    tree.balance()
    missing = np.flatnonzero(~visible)
    for index in missing.tolist():
        mirrored = (-points[index, 0], points[index, 1], points[index, 2])
        _, slot, distance = tree.find(mirrored)
        if distance > .03:
            _, slot, distance = tree.find(points[index])
        colors[index] = colors[indices[slot]]
    return colors


def paint_material(art, ramp_low=.05, ramp_high=.55):
    material = bpy.data.materials.new("ICS_paint")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    attribute = nodes.new("ShaderNodeVertexColor")
    attribute.layer_name = "paint"
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.inputs["Color"].default_value = (1, 1, 1, 1)
    to_rgb = nodes.new("ShaderNodeShaderToRGB")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    elements = ramp.color_ramp.elements
    elements[0].position, elements[0].color = ramp_low, (.72, .68, .7, 1)
    elements[1].position, elements[1].color = ramp_high, (1.08, 1.05, 1.0, 1)
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


# Paleta da prancha (conta-gotas sobre a referência), por peça. Corpo abaixo do queixo = pele.
SKIN = "#B5652F"
PART_COLORS = {
    "belt": "#6B3D22", "waist_cloth": "#E4CFA0", "belt_rope": "#8A5A32", "belt_disc": "#7A4A28",
    "loin_cream_front": "#E4CFA0", "loin_red_tabard": "#B23224", "loin_back": "#C9A878",
    "arm_band": "#6B3D22", "bracer": "#5A3320", "knee_cuff": "#6B3D22", "shin_wrap": "#E4CFA0",
    "sandal_sole": "#5A3320", "sandal_straps": "#6B3D22", "necklace_beads": "#3F342C",
    "necklace_teeth": "#EFE3C4", "shoulder_feathers": "#B9382A", "boot": "#6B3D22",
}


def linear(value):
    return np.where(value <= .04045, value / 12.92, ((value + .055) / 1.055) ** 2.4)


def hex_linear(text):
    rgb = np.array([int(text[i:i + 2], 16) / 255 for i in (1, 3, 5)], dtype=np.float32)
    return linear(rgb)


def part_color(name):
    for prefix, color in PART_COLORS.items():
        if name.startswith(prefix):
            return hex_linear(color)
    return hex_linear(SKIN)


def tree_of(points):
    tree = KDTree(len(points))
    for index, point in enumerate(points.tolist()):
        tree.insert(point, index)
    tree.balance()
    return tree


def run(payload):
    scene = bpy.context.scene
    root = bpy.data.collections["MASTER"]
    guide = bpy.data.objects["guide_b35"]
    image = _image_rgba(payload["reference_rgba"])
    original, b_co = sc._import_b(payload["glb_path"], payload["b_height_m"], payload["yaw_deg"])
    bpy.data.objects.remove(original)

    # Só a cabeça: tem ajuste próprio, porque a pose do corpo na B difere da prancha.
    head = np.flatnonzero(b_co[:, 2] > payload["b_chin"] - .03)
    top = image.copy()
    top[payload["ref_chin_row"]:, :, 3] = 0
    # Setor do rosto voltado ao observador e à direita: só a silhueta confunde frente e perfil.
    (score, degrees, elevation), box = fit_view(b_co[head], top[:, :, 3], (-170, -100))
    colors, visible = sample_colors(b_co[head], top, math.radians(degrees), elevation, box)
    colors = linear(fill_unseen(b_co[head], colors, visible))

    guide_points = read_co(guide.data)[head]
    tree = tree_of(guide_points)
    hair_tree = tree_of(sc._compact_plume(guide_points))
    skin = hex_linear(SKIN)

    body_paint = payload.get("body_paint", False)
    material = paint_material(payload["art"], .08, .85) if body_paint else paint_material(payload["art"])
    outline = mats.flat_material("ICS_paint_outline", (.012, .006, .004))
    outline.use_backface_culling = True
    painted = 0
    for obj in [o for o in root.objects if o.type == "MESH"]:
        if body_paint and obj.name not in ("hair_b", "mouth_b", "master_body"):
            bp.densify(obj)
        points = read_co(obj.data)
        values = np.ones((len(points), 4), dtype=np.float32)
        if obj.name in ("hair_b", "mouth_b", "master_body"):
            use = hair_tree if obj.name == "hair_b" else tree
            sampled = np.zeros((len(points), 3), dtype=np.float32)
            for index, point in enumerate(points.tolist()):
                sampled[index] = colors[use.find(point)[1]]
            if obj.name == "master_body":
                blend = np.clip((points[:, 2] - .905) / .03, 0, 1)[:, None]
                body = bp.skin(*bp.surface(obj.data)) if body_paint else skin
                sampled = sampled * blend + body * (1 - blend)
            values[:, :3] = sampled
        elif body_paint:
            values[:, :3] = bp.paint_part(obj.name, *bp.surface(obj.data))
        else:
            values[:, :3] = part_color(obj.name)
        attribute = obj.data.color_attributes.new("paint", "FLOAT_COLOR", "POINT")
        attribute.data.foreach_set("color", values.ravel())
        obj.data.materials.clear()
        obj.data.materials.append(material)
        for modifier in list(obj.modifiers):
            if modifier.type == "SOLIDIFY":
                obj.modifiers.remove(modifier)
        if body_paint and obj.name != "mouth_b":
            obj.data.materials.append(outline)
            solidify = obj.modifiers.new("ICS_paint_outline", "SOLIDIFY")
            solidify.thickness = payload.get("outline_m", .005)
            solidify.offset = 1.0
            solidify.use_flip_normals = True
            solidify.use_rim = False
            solidify.material_offset = 1
        painted += len(points)

    sun = bpy.data.lights.new("ICS_paint_sun", "SUN")
    sun.energy = payload.get("sun_energy", 3.0)
    light = bpy.data.objects.new("ICS_paint_sun", sun)
    scene.collection.objects.link(light)
    light.rotation_euler = (math.radians(60), 0, math.radians(-30))
    bpy.ops.wm.save_as_mainfile(filepath=payload["blend_path"], compress=True)
    return {
        "fit_iou": score, "phi_deg": degrees, "elevation_deg": elevation,
        "visible_fraction": float(visible.mean()), "painted_vertices": painted,
    }
