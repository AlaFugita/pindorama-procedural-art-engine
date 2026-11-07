"""Rota A: base CC0 → proporção canônica + escultura programada.

Duas operações, ambas preservando a topologia e o UV da base:
1. ``remap_proportions``: leva cada segmento do esqueleto medido na base ao segmento-alvo do
   perfil, com escala radial própria.
2. ``apply_brushes``: pincéis de escultura (deslocamento com queda suave), revistos por render.
"""

import numpy as np


def read_co(mesh):
    co = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", co)
    return co.reshape(-1, 3)


def write_co(mesh, co):
    mesh.vertices.foreach_set("co", co.ravel())
    mesh.update()


def to_canonical(co):
    """A base olha para -Y; o projeto olha para +Y (doc 17). Giro de 180° em Z."""
    out = co.copy()
    out[:, 0] *= -1
    out[:, 1] *= -1
    return out


def edge_array(mesh):
    edges = np.empty(len(mesh.edges) * 2, dtype=np.int32)
    mesh.edges.foreach_get("vertices", edges)
    return edges.reshape(-1, 2)


def smooth_field(field, edges, iterations, factor=0.5):
    count = np.zeros(len(field))
    np.add.at(count, edges.ravel(), 1)
    for _ in range(iterations):
        total = np.zeros_like(field)
        np.add.at(total, edges[:, 0], field[edges[:, 1]])
        np.add.at(total, edges[:, 1], field[edges[:, 0]])
        field = field + factor * (total / count[:, None] - field)
    return field


def _expand(segments):
    """Espelha segmentos ``s``: lado direito (+X) e esquerdo (-X) em coordenadas canônicas."""
    result = []
    for seg in segments:
        if seg.get("mirror"):
            for sign, side in ((1.0, "R"), (-1.0, "L")):
                flip = np.array([sign, 1.0, 1.0])
                result.append({
                    **seg, "name": f"{seg['name']}_{side}", "side": side,
                    "src": [np.array(p) * flip for p in seg["src"]],
                    "dst": [np.array(p) * flip for p in seg["dst"]],
                })
        else:
            result.append({**seg, "side": "C",
                           "src": [np.array(p, float) for p in seg["src"]],
                           "dst": [np.array(p, float) for p in seg["dst"]]})
    return result


def _rotation_between(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k / (1 + c)


def segment_transform(points, seg):
    a, b = seg["src"]
    a2, b2 = seg["dst"]
    axis = b - a
    length2 = float(axis @ axis)
    t = ((points - a) @ axis) / length2
    clamped = np.clip(t, 0, 1)
    along = a + clamped[:, None] * axis
    offset = points - along
    extra = t - clamped
    offset = offset - extra[:, None] * axis  # a sobra fora do segmento entra como eixo
    rx = seg["rx"][0] + (seg["rx"][1] - seg["rx"][0]) * clamped
    ry = seg["ry"][0] + (seg["ry"][1] - seg["ry"][0]) * clamped
    rotation = _rotation_between(axis, b2 - a2)
    local = offset * np.column_stack((rx, ry, (rx + ry) / 2))
    moved = local @ rotation.T
    new_axis = b2 - a2
    ratio = np.linalg.norm(new_axis) / np.sqrt(length2)
    return (a2 + clamped[:, None] * new_axis + moved
            + (extra * ratio * np.sqrt(length2))[:, None] * (new_axis / np.linalg.norm(new_axis)))


def segment_distance(points, seg):
    a, b = seg["src"]
    axis = b - a
    t = np.clip(((points - a) @ axis) / float(axis @ axis), 0, 1)
    return np.linalg.norm(points - (a + t[:, None] * axis), axis=1)


def remap_proportions(points, segments, side_band=0.03, power=7.0):
    segments = _expand(segments)
    weights = np.zeros((len(points), len(segments)))
    moved = np.zeros((len(points), len(segments), 3))
    for index, seg in enumerate(segments):
        distance = segment_distance(points, seg) / seg["influence"]
        weight = (distance + 1e-3) ** -power
        if seg["side"] == "R":
            weight[points[:, 0] < -side_band] = 0
        if seg["side"] == "L":
            weight[points[:, 0] > side_band] = 0
        weights[:, index] = weight
        moved[:, index] = segment_transform(points, seg)
    weights /= weights.sum(axis=1, keepdims=True)
    return (weights[..., None] * moved).sum(axis=1)


def apply_warps(points, warps, eye_centers):
    """Deformação local por escala e translação, com queda suave; preserva a topologia."""
    result = points.copy()
    for warp in warps:
        centers = eye_centers if isinstance(warp["c"], str) else [np.array(warp["c"], float)]
        for center in centers:
            distance = np.linalg.norm(result - center, axis=1) / warp["r"]
            falloff = (np.clip(1 - distance ** 2, 0, 1) ** 2)[:, None]
            if "scale" in warp:
                result = result + falloff * (result - center) * (warp["scale"] - 1)
            if "move" in warp:
                result = result + falloff * np.array(warp["move"], float)
    return result


def vertex_normals(co, polygons_flat, loop_starts, loop_totals):
    """Normal por vértice a partir de quads (Newell simplificado por fan)."""
    normals = np.zeros_like(co)
    a = polygons_flat[loop_starts]
    b = polygons_flat[loop_starts + 1]
    c = polygons_flat[loop_starts + loop_totals - 1]
    face = np.cross(co[b] - co[a], co[c] - co[a])
    for corner in (a, b, c):
        np.add.at(normals, corner, face)
    length = np.linalg.norm(normals, axis=1, keepdims=True)
    return normals / np.maximum(length, 1e-12)


def mesh_topology(mesh):
    loops = np.empty(len(mesh.loops), dtype=np.int32)
    mesh.loops.foreach_get("vertex_index", loops)
    starts = np.empty(len(mesh.polygons), dtype=np.int32)
    totals = np.empty(len(mesh.polygons), dtype=np.int32)
    mesh.polygons.foreach_get("loop_start", starts)
    mesh.polygons.foreach_get("loop_total", totals)
    return loops, starts, totals


def apply_brushes(co, brushes, topology, edges, region=None):
    """Cada pincel: c, r, a; dir opcional (senão normal); ell escala anisotrópica da distância."""
    loops, starts, totals = topology
    result = co.copy()
    for brush in brushes:
        normals = vertex_normals(result, loops, starts, totals)
        signs = (1.0, -1.0) if brush.get("mirror") else (1.0,)
        for sign in signs:
            center = np.array(brush["c"], float) * np.array([sign, 1.0, 1.0])
            ellipse = np.array(brush.get("ell", (1, 1, 1)), float)
            distance = np.linalg.norm((result - center) / ellipse, axis=1) / brush["r"]
            falloff = np.clip(1 - distance ** 2, 0, 1) ** 2
            if region is not None:
                falloff = falloff * region
            if "dir" in brush:
                direction = np.array(brush["dir"], float) * np.array([sign, 1.0, 1.0])
                result = result + falloff[:, None] * direction * brush["a"]
            else:
                result = result + falloff[:, None] * normals * brush["a"]
        if brush.get("relax"):
            delta = smooth_field(result, edges, brush["relax"], .3) - result
            mask = np.clip(1 - np.linalg.norm(result - np.array(brush["c"], float), axis=1) / (brush["r"] * 1.2), 0, 1)
            result = result + delta * mask[:, None]
    return result


# Medidas tiradas da base (docs/audit/master_prototype/) já em coordenadas canônicas.
SEGMENTS = [
    {"name": "head", "src": [(0, 0, 1.4775), (0, 0, 1.795)], "dst": [(0, 0, .929), (0, 0, 1.30)],
     "rx": (1.14, 1.14), "ry": (1.14, 1.14), "influence": .17},
    {"name": "neck", "src": [(0, .02, 1.41), (0, 0, 1.4775)], "dst": [(0, .01, .875), (0, 0, .929)],
     "rx": (1.45, 1.4), "ry": (1.4, 1.35), "influence": .07},
    {"name": "chest", "src": [(0, 0, 1.20), (0, 0, 1.42)], "dst": [(0, 0, .70), (0, .01, .875)],
     "rx": (1.15, 1.2), "ry": (1.25, 1.2), "influence": .14},
    {"name": "spine", "src": [(0, 0, 1.03), (0, 0, 1.20)], "dst": [(0, 0, .585), (0, 0, .70)],
     "rx": (1.08, 1.15), "ry": (1.15, 1.25), "influence": .13},
    {"name": "pelvis", "src": [(0, 0, .93), (0, 0, 1.03)], "dst": [(0, 0, .47), (0, 0, .585)],
     "rx": (1.1, 1.08), "ry": (1.1, 1.15), "influence": .12},
    {"name": "clav", "mirror": True, "src": [(.05, 0, 1.40), (.19, 0, 1.37)],
     "dst": [(.05, 0, .84), (.215, 0, .805)], "rx": (1.2, 1.3), "ry": (1.2, 1.3), "influence": .08},
    {"name": "upper_arm", "mirror": True, "src": [(.19, 0, 1.37), (.345, 0, 1.09)],
     "dst": [(.215, 0, .805), (.305, 0, .575)], "rx": (1.3, 1.25), "ry": (1.3, 1.25), "influence": .08},
    {"name": "forearm", "mirror": True, "src": [(.345, 0, 1.09), (.405, 0, .90)],
     "dst": [(.305, 0, .575), (.355, .012, .395)], "rx": (1.35, 1.45), "ry": (1.35, 1.45), "influence": .07},
    {"name": "hand", "mirror": True, "src": [(.405, 0, .90), (.415, 0, .68)],
     "dst": [(.355, .012, .395), (.378, .02, .225)], "rx": (1.35, 1.2), "ry": (1.2, 1.2), "influence": .08},
    {"name": "thigh", "mirror": True, "src": [(.095, 0, .93), (.082, .01, .50)],
     "dst": [(.10, 0, .47), (.105, .012, .27)], "rx": (1.2, 1.12), "ry": (1.2, 1.1), "influence": .1},
    {"name": "shin", "mirror": True, "src": [(.082, .01, .50), (.095, 0, .10)],
     "dst": [(.105, .012, .27), (.11, 0, .08)], "rx": (1.15, 1.25), "ry": (1.12, 1.2), "influence": .07},
    {"name": "foot", "mirror": True, "src": [(.095, 0, .09), (.115, .19, .02)],
     "dst": [(.11, 0, .075), (.128, .205, .018)], "rx": (1.25, 1.3), "ry": (.85, .85), "influence": .08},
]
