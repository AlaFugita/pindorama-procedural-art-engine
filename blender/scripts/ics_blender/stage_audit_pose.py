"""Sonda de auditoria: chão e interseção coxa × túnica em todos os quadros de todos os clips.

Mede a malha deformada sem a casca de contorno (Solidify desligado só na avaliação).
- ``min_z``: ponto mais baixo de cada peça por clip (negativo = abaixo do chão);
- ``thigh_out``: vértices das coxas fora do contorno da túnica na mesma fatia de altura.
"""

import bpy
from mathutils import Vector
from mathutils.geometry import convex_hull_2d

from . import animation as anim

SKIRT = ("tunic", "tunic_hem")
SLICE = .012
MARGIN_Z = .03


def _segment_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (p - (a + ab * t)).length


def _inside(poly, p):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > p[1]) != (yj > p[1]) and p[0] < (xj - xi) * (p[1] - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def _world_verts(obj, depsgraph, edges=None):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    verts = [ev.matrix_world @ v.co for v in mesh.vertices]
    if edges is not None:
        edges += [(verts[e.vertices[0]], verts[e.vertices[1]]) for e in mesh.edges]
    ev.to_mesh_clear()
    return verts


def _section(edges, z):
    """Pontos onde as arestas cruzam o plano horizontal z."""
    out = []
    for a, b in edges:
        if (a.z - z) * (b.z - z) <= 0 and a.z != b.z:
            t = (z - a.z) / (b.z - a.z)
            out.append((a + (b - a) * t).to_2d())
    return out


def run(payload):
    scene = bpy.context.scene
    armature = bpy.data.objects["ICS_Rig"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for obj in meshes:
        for mod in obj.modifiers:
            if mod.type == "SOLIDIFY":
                mod.show_viewport = False
    body = bpy.data.objects["body"]
    groups = {g.index: g.name for g in body.vertex_groups}
    thigh = [v.index for v in body.data.vertices
             if sum(e.weight for e in v.groups if groups.get(e.group, "").startswith("thigh")) > .5]
    report = {"thigh_vertices": len(thigh), "clips": {}}
    for action in sorted(a.name for a in bpy.data.actions if a.name.startswith("clip_")):
        frames = int(anim.use_action(armature, action).frame_range[1])
        lows, outside = {}, []
        for frame in range(frames):
            scene.frame_set(frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            skirt, skirt_edges = [], []
            for obj in meshes:
                verts = _world_verts(obj, depsgraph, skirt_edges if obj.name in SKIRT else None)
                low = min(v.z for v in verts)
                if obj.name not in lows or low < lows[obj.name][0]:
                    lows[obj.name] = (round(low, 4), frame)
                if obj.name in SKIRT:
                    skirt += verts
            legs = _world_verts(body, depsgraph)
            count, worst = 0, 0.0
            top = max(v.z for v in skirt)
            # Só conta onde o tecido cobre por inteiro: acima da barra, abaixo da cintura.
            bottom = min(v.z for v in skirt) + MARGIN_Z
            for i in thigh:
                p = legs[i]
                if p.z > top or p.z < bottom:
                    continue
                ring = _section(skirt_edges, p.z)
                if len(ring) < 8:
                    continue
                poly = [ring[k] for k in convex_hull_2d(ring)]
                q = p.to_2d()
                if not _inside(poly, q):
                    gap = min(_segment_distance(q, poly[k - 1], poly[k]) for k in range(len(poly)))
                    if gap > worst:
                        worst = gap
                        where = {"world": [round(c, 3) for c in p], "rest": [round(c, 3) for c in body.data.vertices[i].co],
                                 "ring_x": [round(min(v.x for v in poly), 3), round(max(v.x for v in poly), 3)],
                                 "ring_y": [round(min(v.y for v in poly), 3), round(max(v.y for v in poly), 3)]}
                    count += 1
            outside.append({"vertices": count, "max_mm": round(worst * 1000, 1), **({"worst": where} if count else {})})
        name = action.removeprefix("clip_")
        report["clips"][name] = {
            "frames": frames,
            "min_z": {k: v for k, v in sorted(lows.items(), key=lambda kv: kv[1][0])},
            "thigh_out_per_frame": outside,
        }
    return report
