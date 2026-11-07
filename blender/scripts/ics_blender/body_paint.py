"""Pintura do corpo por vértice: volumes, desgaste e grafismos, sem imagem de terceiros.

A luz pintada usa só a inclinação vertical e a curvatura. Nenhuma das duas depende do giro do
personagem, então a pintura segue válida nas oito direções. Grafismos vêm de coordenadas da peça.
"""

import bpy
import numpy as np

from . import master_body as mb
from .scene import hex_to_linear


def rgb(value):
    return np.array(hex_to_linear(value), dtype=np.float64)


SKIN_MID = rgb("#A05426")
SKIN_DARK = rgb("#551F0E")
SKIN_LIGHT = rgb("#C98347")
CREAM = rgb("#D8BE8A")
CREAM_DIRT = rgb("#A9835A")
RED = rgb("#B23224")
RED_DARK = rgb("#6E1A14")
ORANGE = rgb("#DD7E22")
LEATHER = rgb("#6B3D22")
LEATHER_DARK = rgb("#2E1A10")
LEATHER_LIGHT = rgb("#A06A3A")
BRASS = rgb("#C49A4A")
TEAL = rgb("#3F6A68")
BONE = rgb("#EFE3C4")
INK = rgb("#24140D")


def mix(a, b, t):
    t = np.clip(t, 0, 1)[..., None] if np.ndim(t) else float(np.clip(t, 0, 1))
    return a * (1 - t) + b * t


def noise(co, scale=1.0):
    """Ruído suave determinístico, em [-1, 1]."""
    p = co * scale
    value = (np.sin(p[:, 0] * 41 + p[:, 2] * 17) + np.sin(p[:, 1] * 29 - p[:, 2] * 53)
             + np.sin(p[:, 0] * 91 + p[:, 1] * 73 + p[:, 2] * 37) * .6)
    return value / 2.6


def densify(obj, target_vertices=9000):
    """Subdivisão simples nesta cópia: cor por vértice precisa de densidade para desenhar."""
    levels = 0
    count = len(obj.data.vertices)
    while count * 4 ** levels < target_vertices and levels < 4:
        levels += 1
    if levels == 0:
        return
    modifier = obj.modifiers.new("densify", "SUBSURF")
    modifier.subdivision_type = "SIMPLE"
    modifier.levels = levels
    modifier.render_levels = levels
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.remove(modifier)
    obj.data = mesh
    mesh.shade_smooth()


def surface(mesh):
    co = mb.read_co(mesh)
    normals = mb.vertex_normals(co, *mb.mesh_topology(mesh))
    edges = mb.edge_array(mesh)
    fine = ((mb.smooth_field(co, edges, 2, .5) - co) * normals).sum(axis=1)
    broad = ((mb.smooth_field(co, edges, 40, .5) - co) * normals).sum(axis=1)
    return co, normals, fine, broad


def shade(colors, normals, fine, broad, dark, light, strength=1.0):
    """Reentrâncias escurecem, relevos e faces para cima clareiam. Independe do giro."""
    up = normals[:, 2]
    amount = (-up * .3 + broad * 62 + fine * 380) * strength
    shadow = mix(colors, dark, np.clip(amount, 0, 1))
    return mix(shadow, light, np.clip(-amount * .85, 0, .75))


def skin(co, normals, fine, broad):
    colors = np.tile(SKIN_MID, (len(co), 1))
    colors = mix(colors, rgb("#B3622C"), .5 + noise(co, .35) * .5)
    colors = shade(colors, normals, fine, broad, SKIN_DARK, SKIN_LIGHT, 1.25)
    # Faixa clara do ombro e marcas de pintura corporal.
    x, z = np.abs(co[:, 0]), co[:, 2]
    colors[(x > .22) & (x < .29) & (z > .69) & (z < .735)] = CREAM * .9
    return colors


def cloth(co, normals, fine, broad, hem_z):
    colors = mix(CREAM, CREAM_DIRT, np.clip((hem_z + .12 - co[:, 2]) / .22, 0, 1) * .55)
    colors = mix(colors, CREAM_DIRT, np.clip(noise(co, .8) * .55, 0, .4))
    weave = np.abs(np.sin(co[:, 0] * 420)) < .1
    colors[weave] = colors[weave] * .92
    return shade(colors, normals, fine, broad, CREAM_DIRT * .6, CREAM, .9)


def tabard(co, normals, fine, broad):
    """Faixa vermelha: moldura creme, losango central e barra em dentes."""
    x, z = co[:, 0], co[:, 2]
    colors = np.tile(RED, (len(co), 1))
    colors = mix(colors, RED_DARK, np.clip(noise(co, .5) * .5 + .15, 0, .4))
    edge = .055 - np.abs(x)
    colors[edge < .010] = CREAM
    colors[(edge >= .010) & (edge < .014)] = INK
    colors[(edge >= .019) & (edge < .024) & (z > .315) & (z < .52)] = CREAM
    middle = np.abs(x) + np.abs(z - .44) * .62
    colors[(middle > .022) & (middle < .03)] = CREAM
    colors[z < .305] = CREAM
    band = np.abs(z - .305) < .005
    colors[band] = INK
    teeth = (z < .285) & (np.abs(((x + .1) % .022) - .011) * 1.5 > (z - .262))
    colors[teeth] = RED
    return shade(colors, normals, fine, broad, RED_DARK * .55, CREAM, .75)


def around(co, a, b):
    a, b = np.array(a, float), np.array(b, float)
    axis = (b - a) / np.linalg.norm(b - a)
    t = (co - a) @ axis / np.linalg.norm(b - a)
    helper = np.array([1.0, 0, 0]) if abs(axis[0]) < .9 else np.array([0, 1.0, 0])
    u = np.cross(axis, helper)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    return t, np.arctan2((co - a) @ v, (co - a) @ u)


def bracer(co, normals, fine, broad, sign):
    t, angle = around(co, (sign * .305, 0, .575), (sign * .355, .012, .395))
    colors = np.tile(LEATHER, (len(co), 1))
    colors = mix(colors, LEATHER_LIGHT, np.clip(noise(co, .7) * .6 + .2, 0, .5))
    lattice = (np.abs(np.sin(angle * 5 + t * 18)) < .17) | (np.abs(np.sin(angle * 5 - t * 18)) < .17)
    inner = (t > .56) & (t < .95)
    colors[lattice & inner] = LEATHER_DARK
    colors[np.abs(t - .55) < .035] = LEATHER_LIGHT
    colors[np.abs(t - .96) < .035] = LEATHER_LIGHT
    return shade(colors, normals, fine, broad, LEATHER_DARK, LEATHER_LIGHT, 1.0)


def arm_band(co, normals, fine, broad, sign):
    t, angle = around(co, (sign * .215, 0, .805), (sign * .305, 0, .575))
    colors = np.tile(LEATHER, (len(co), 1))
    colors[np.abs(np.sin(angle * 7)) < .2] = LEATHER_DARK
    colors[np.abs(t - .6) < .012] = LEATHER_LIGHT
    colors[np.abs(t - .76) < .012] = LEATHER_LIGHT
    return shade(colors, normals, fine, broad, LEATHER_DARK, LEATHER_LIGHT, 1.0)


def leather(co, normals, fine, broad, base=LEATHER):
    colors = mix(base, LEATHER_LIGHT, np.clip(noise(co, .9) * .5 + .15, 0, .45))
    return shade(colors, normals, fine, broad, LEATHER_DARK, LEATHER_LIGHT, 1.1)


def wrap(co, normals, fine, broad):
    colors = mix(CREAM, CREAM_DIRT, np.clip(noise(co, .9) * .5 + .1, 0, .4))
    return shade(colors, normals, fine, broad, CREAM_DIRT * .55, CREAM, 1.0)


def belt_disc(co, normals, fine, broad):
    radius = np.hypot(co[:, 0], co[:, 2] - .553)
    colors = np.tile(BRASS, (len(co), 1))
    colors[radius < .03] = LEATHER
    colors[radius < .012] = BRASS
    colors[np.abs(radius - .031) < .004] = INK
    return shade(colors, normals, fine, broad, LEATHER_DARK, BONE, 1.0)


def feathers(co, normals, fine, broad):
    sign = np.where(co[:, 0] >= 0, 1.0, -1.0)
    root = np.column_stack((sign * .19, np.zeros(len(co)), np.full(len(co), .84)))
    reach = np.linalg.norm(co - root, axis=1) / .22
    colors = mix(RED_DARK, RED, np.clip(reach * 2.2, 0, 1))
    colors = mix(colors, ORANGE, np.clip((reach - .93) * 5, 0, .55))
    colors[np.abs(np.sin(reach * 54)) < .11] *= .72
    return shade(colors, normals, fine, broad, RED_DARK * .5, ORANGE, 1.0)


def beads(co, normals, fine, broad):
    colors = np.tile(LEATHER, (len(co), 1))
    colors[np.sin(co[:, 0] * 74) > .1] = TEAL
    colors[np.sin(co[:, 0] * 74) < -.75] = BONE
    return shade(colors, normals, fine, broad, INK, BONE, .8)


def bone(co, normals, fine, broad):
    colors = mix(BONE, CREAM_DIRT, np.clip((.76 - co[:, 2]) / .08, 0, .35))
    return shade(colors, normals, fine, broad, CREAM_DIRT * .6, BONE, 1.0)


def paint_part(name, co, normals, fine, broad):
    sign = 1.0 if name.endswith("_R") else -1.0
    if name == "loin_red_tabard":
        return tabard(co, normals, fine, broad)
    if name.startswith("loin_cream"):
        return cloth(co, normals, fine, broad, .27)
    if name.startswith("loin_back"):
        return cloth(co, normals, fine, broad, .29) * .9
    if name.startswith("waist_cloth"):
        return cloth(co, normals, fine, broad, .3)
    if name.startswith("bracer"):
        return bracer(co, normals, fine, broad, sign)
    if name.startswith("arm_band"):
        return arm_band(co, normals, fine, broad, sign)
    if name.startswith("shin_wrap"):
        return wrap(co, normals, fine, broad)
    if name.startswith("belt_disc"):
        return belt_disc(co, normals, fine, broad)
    if name.startswith("shoulder_feathers"):
        return feathers(co, normals, fine, broad)
    if name.startswith("necklace_beads"):
        return beads(co, normals, fine, broad)
    if name.startswith("necklace_teeth"):
        return bone(co, normals, fine, broad)
    if name.startswith("sandal_sole"):
        return leather(co, normals, fine, broad, LEATHER_DARK)
    return leather(co, normals, fine, broad)
