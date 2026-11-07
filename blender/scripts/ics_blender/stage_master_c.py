"""Rota C: forma da Rota B sobre a estrutura da Rota A.

1. Importa a malha da B e a leva às proporções canônicas com o mesmo remapeamento da A.
2. Projeta a topologia da base CC0 sobre o rosto da B (preserva quads e UV).
3. Recorta da B o cabelo e as penas, como peça separada, no lugar do cabelo procedural.

As articulações de origem da B são lidas na malha, então valem para esta geração específica.
"""

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from . import master_body as mb

A_CHIN, A_TOP = .9217, 1.2956


def b_segments(b_chin, b_top):
    scale = (A_TOP - A_CHIN) / (b_top - b_chin)
    return [
        {"name": "head", "src": [(0, 0, b_chin), (0, 0, b_top)], "dst": [(0, 0, A_CHIN), (0, 0, A_TOP)],
         "rx": (scale, scale), "ry": (scale, scale), "influence": .2},
        {"name": "neck", "src": [(0, 0, 1.03), (0, 0, b_chin)], "dst": [(0, 0, .875), (0, 0, A_CHIN)],
         "rx": (1.1, 1.1), "ry": (1.1, 1.1), "influence": .07},
        {"name": "chest", "src": [(0, 0, .84), (0, 0, 1.03)], "dst": [(0, 0, .70), (0, 0, .875)],
         "rx": (1.1, 1.1), "ry": (1.1, 1.1), "influence": .14},
        {"name": "spine", "src": [(0, 0, .74), (0, 0, .84)], "dst": [(0, 0, .585), (0, 0, .70)],
         "rx": (1.05, 1.1), "ry": (1.05, 1.1), "influence": .13},
        {"name": "pelvis", "src": [(0, 0, .64), (0, 0, .74)], "dst": [(0, 0, .47), (0, 0, .585)],
         "rx": (1.05, 1.05), "ry": (1.05, 1.05), "influence": .12},
        {"name": "clav", "mirror": True, "src": [(.05, 0, 1.02), (.18, 0, 1.0)],
         "dst": [(.05, 0, .84), (.215, 0, .805)], "rx": (1.1, 1.1), "ry": (1.1, 1.1), "influence": .08},
        {"name": "upper_arm", "mirror": True, "src": [(.18, 0, 1.0), (.265, 0, .79)],
         "dst": [(.215, 0, .805), (.305, 0, .575)], "rx": (1.1, 1.1), "ry": (1.1, 1.1), "influence": .09},
        {"name": "forearm", "mirror": True, "src": [(.265, 0, .79), (.26, 0, .66)],
         "dst": [(.305, 0, .575), (.355, .012, .395)], "rx": (1.1, 1.1), "ry": (1.1, 1.1), "influence": .08},
        {"name": "hand", "mirror": True, "src": [(.26, 0, .66), (.255, 0, .55)],
         "dst": [(.355, .012, .395), (.378, .02, .225)], "rx": (1.2, 1.2), "ry": (1.2, 1.2), "influence": .08},
        {"name": "thigh", "mirror": True, "src": [(.09, 0, .64), (.115, 0, .42)],
         "dst": [(.10, 0, .47), (.105, .012, .27)], "rx": (1.05, 1.05), "ry": (1.05, 1.05), "influence": .11},
        {"name": "shin", "mirror": True, "src": [(.115, 0, .42), (.15, 0, .11)],
         "dst": [(.105, .012, .27), (.11, 0, .08)], "rx": (1.05, 1.05), "ry": (1.05, 1.05), "influence": .08},
    ]

# hair_mass também sai: em t04 ela atravessou o cabelo da Rota B.
SOURCE_HAIR = {"hair", "hair_mass", "hair_tie", "crown_feathers", "earrings"}


def _import_b(path, height, yaw_deg):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    obj = next(o for o in set(bpy.data.objects) - before if o.type == "MESH")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    matrix = np.array(obj.evaluated_get(depsgraph).matrix_world)
    co = mb.read_co(obj.data) @ matrix[:3, :3].T + matrix[:3, 3]
    yaw = np.radians(yaw_deg)
    rotation = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
    co = (co * (height / (co[:, 2].max() - co[:, 2].min()))) @ rotation.T
    center = (co.max(axis=0) + co.min(axis=0)) / 2
    co -= (center[0], center[1], co[:, 2].min())
    for other in [o for o in set(bpy.data.objects) - before if o is not obj]:
        bpy.data.objects.remove(other)
    return obj, co


def _face_mask(co):
    """Região projetada: frente do rosto até a linha do cabelo, com bordas suaves."""
    front = np.clip((co[:, 1] - .03) / .05, 0, 1)
    top = np.clip((1.15 - co[:, 2]) / .03, 0, 1)  # para na sobrancelha: a testa fica sob o cabelo
    bottom = np.clip((co[:, 2] - .922) / .02, 0, 1)  # termina no queixo: abaixo disso é pescoço da A
    side = np.clip((.15 - np.abs(co[:, 0])) / .03, 0, 1)
    return front * top * bottom * side


def _project(co, tree, mask, edges, passes):
    """Alterna relaxar e projetar: tira olhos, narinas e boca de dentro antes de assentar."""
    result = co.copy()
    selected = np.flatnonzero(mask > 0)
    for step in range(passes):
        relaxed = mb.smooth_field(result, edges, 10 if step < passes - 2 else 2, .5)
        result = result + (relaxed - result) * mask[:, None]
        delta = np.zeros_like(result)
        for index in selected:
            hit = tree.find_nearest(Vector(result[index]))[0]
            if hit is not None:
                delta[index] = np.array(hit) - result[index]
        result = result + mb.smooth_field(delta * mask[:, None], edges, 1, .5)
    # Assentamento final, sem suavizar. Raios frontais foram testados (t04) e pioraram: pegam
    # mechas que passam na frente do rosto.
    delta = np.zeros_like(result)
    for index in np.flatnonzero(mask > .5):
        hit = tree.find_nearest(Vector(result[index]))[0]
        if hit is not None:
            delta[index] = np.array(hit) - result[index]
    return result + delta * mask[:, None]


def _hair_keep(points, skin_tree, body_co, mask, gap, crop):
    """Mantém a cabeça da B, menos a pele do rosto e as abas nascidas da máscara de entrada."""
    keep = points[:, 2] > .93
    if crop:
        # Só para entradas com aba e placa nascidas do corte da máscara (malha seed42_v3).
        inside = (np.abs(points[:, 0]) < .19) & (points[:, 1] > -.22)
        keep &= (points[:, 2] > 1.29) | inside
    # Sobras de pescoço e ombro que a B funde ao cabelo.
    keep &= ~((points[:, 2] < 1.0) & (points[:, 1] > -.16))
    head_vertices = np.flatnonzero(keep)
    # Pele da B: perto da pele projetada, dentro da máscara do rosto.
    from mathutils.kdtree import KDTree

    tree = KDTree(len(body_co))
    for index, value in enumerate(body_co):
        tree.insert(value, index)
    tree.balance()
    for index in head_vertices.tolist():
        location, _, _, distance = skin_tree.find_nearest(Vector(points[index]))
        if distance is None:
            continue
        nearest = tree.find(location)[1]
        in_face = abs(points[index, 0]) < .135 and points[index, 1] > .02 and points[index, 2] < 1.17
        limit = gap * 2.2 if points[index, 2] < 1.125 else gap  # manchas de pele junto aos olhos
        if in_face and mask[nearest] > .2 and distance < limit:
            keep[index] = False
    return keep


def _compact_plume(points):
    """A B inflou a pluma atrás da cabeça: recolhe só o que está além da nuca."""
    result = points.copy()
    behind = np.clip((-.17 - result[:, 1]) / .3, 0, 1)
    result[:, 1] = result[:, 1] + (behind * .3) * .45
    result[:, 2] = result[:, 2] + behind * .05
    return result


def _chunk(name, points, faces, keep, root, target_faces):
    chosen = faces[keep[faces].all(axis=1)]
    used, inverse = np.unique(chosen, return_inverse=True)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points[used].tolist(), [], inverse.reshape(-1, 3).tolist())
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    root.objects.link(obj)
    modifier = obj.modifiers.new("decimate", "DECIMATE")
    modifier.ratio = min(1.0, target_faces / max(len(mesh.polygons), 1))
    depsgraph = bpy.context.evaluated_depsgraph_get()
    reduced = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()
    obj.data = reduced
    reduced.shade_smooth()
    return obj


def run(payload):
    scene = bpy.context.scene
    root = bpy.data.collections["MASTER"]
    b_obj, b_co = _import_b(payload["glb_path"], payload["b_height_m"], payload["yaw_deg"])
    segments = b_segments(payload["b_chin"], payload["b_top"])
    remapped = mb.remap_proportions(b_co, segments, side_band=.03, power=7.0)
    faces = np.empty(len(b_obj.data.polygons) * 3, dtype=np.int32)
    b_obj.data.polygons.foreach_get("vertices", faces)
    faces = faces.reshape(-1, 3)

    body = bpy.data.objects["master_body"]
    co = mb.read_co(body.data)
    # Alinha nariz e centro antes de projetar: pequeno ajuste só da região da cabeça da B.
    head_zone = remapped[:, 2] > .92
    a_nose = co[(np.abs(co[:, 0]) < .03) & (co[:, 2] > 1.0) & (co[:, 2] < 1.1)][:, 1].max()
    b_face = remapped[head_zone & (np.abs(remapped[:, 0]) < .03) & (remapped[:, 2] < 1.1)]
    b_nose = b_face[:, 1].max()
    shift = np.array([0.0, a_nose - b_nose + payload.get("nudge_y", 0.0), 0.0])
    falloff = np.clip((remapped[:, 2] - .88) / .05, 0, 1)
    remapped = remapped + falloff[:, None] * shift
    print("MC nariz A", a_nose, "B", b_nose, "desvio", shift[1])

    tree = BVHTree.FromPolygons(remapped.tolist(), faces.tolist(), all_triangles=True)
    edges = mb.edge_array(body.data)
    mask = _face_mask(co)
    wrapped = _project(co, tree, mask, edges, payload.get("passes", 8))
    mb.write_co(body.data, wrapped)
    body.data.shade_smooth()

    # Remove peças que a B passa a fornecer; os globos oculares ficam fora em argila.
    for name in list(SOURCE_HAIR) + ["GEO-body_male_stylized.eye.L", "GEO-body_male_stylized.eye.R"]:
        target = bpy.data.objects.get(name)
        if target is not None:
            bpy.data.objects.remove(target)

    # Cabelo: tudo da cabeça da B que não é pele projetada.
    skin = BVHTree.FromPolygons(wrapped.tolist(), [tuple(p.vertices) for p in body.data.polygons])
    keep = _hair_keep(remapped, skin, wrapped, mask, payload.get("hair_gap_m", .009), payload.get("hair_crop", False))
    hair_points = _compact_plume(remapped)
    hair_mesh = _chunk("hair_b", hair_points, faces, keep, root, payload.get("hair_faces", 40000)).data

    # Remendo da boca: o interior da base achata com faces invertidas. A superfície da B cobre.
    pieces = {}
    mouth = (np.abs(remapped[:, 0]) < .062) & (remapped[:, 2] > .98) & (remapped[:, 2] < 1.04) \
        & (remapped[:, 1] > .1)
    patch = remapped + np.array((0, .0015, 0))
    pieces["mouth_b"] = _chunk("mouth_b", patch, faces, mouth, root, 4000)

    # Punhos e colar por recorte falharam (t07): a pele da B não se separa dos ornamentos.
    # Ficam desligados; usar `transplant` só para reproduzir a tentativa.
    for side, sign in (("r", 1.0), ("l", -1.0)) if payload.get("transplant") else ():
        wrist = np.array((sign * .355, .012, .395))
        tip = np.array((sign * .378, .02, .225))
        axis = tip - wrist
        t = np.clip((remapped - wrist) @ axis / (axis @ axis), 0, 1)
        distance = np.linalg.norm(remapped - (wrist + t[:, None] * axis), axis=1)
        zone = (distance < .1) & (remapped[:, 2] < .375) & (np.sign(remapped[:, 0]) == sign)
        pieces[f"fist_{side}"] = _chunk(f"fist_{side}", remapped, faces, zone, root, 12000)
        hand = (np.sign(wrapped[:, 0]) == sign) & (wrapped[:, 2] < .39) & (np.abs(wrapped[:, 0]) > .28)
        wrapped[hand] = wrist + (wrapped[hand] - wrist) * .35
    mb.write_co(body.data, wrapped)
    if payload.get("transplant"):
        distance_zone = (remapped[:, 2] > .72) & (remapped[:, 2] < .875) & (remapped[:, 1] > .05) \
            & (np.abs(remapped[:, 0]) < .15)
        for index in np.flatnonzero(distance_zone).tolist():
            _, _, _, distance = skin.find_nearest(Vector(remapped[index]))
            distance_zone[index] = distance is not None and distance > .012
        pieces["necklace_b"] = _chunk("necklace_b", remapped, faces, distance_zone, root, 12000)
        for name in ("necklace_beads", "necklace_teeth"):
            target = bpy.data.objects.get(name)
            if target is not None:
                bpy.data.objects.remove(target)

    # Guarda a B reproporcionada como referência oculta para comparação.
    mb.write_co(b_obj.data, remapped)
    b_obj.name = "guide_b35"
    for owner in list(b_obj.users_collection):
        owner.objects.unlink(b_obj)
    guide = bpy.data.collections.new("GUIDE")
    scene.collection.children.link(guide)
    guide.objects.link(b_obj)
    guide.hide_render = True
    bpy.ops.wm.save_as_mainfile(filepath=payload["blend_path"], compress=True)
    return {
        "head_scale": segments[0]["rx"][0], "nose_shift_m": float(shift[1]),
        "body_vertices": len(body.data.vertices), "hair_faces": len(hair_mesh.polygons),
        "pieces": {k: len(v.data.polygons) for k, v in pieces.items()},
        "projected_vertices": int((mask > 0).sum()),
    }
