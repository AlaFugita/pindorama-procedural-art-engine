"""Primitivas procedurais em coordenadas canônicas. Retornam (verts, faces) simples."""

import math

from mathutils import Vector


def merge(*meshes):
    verts, faces = [], []
    for mesh_verts, mesh_faces in meshes:
        offset = len(verts)
        verts.extend(mesh_verts)
        faces.extend(tuple(i + offset for i in face) for face in mesh_faces)
    return verts, faces


def _frame(direction):
    axis = Vector(direction).normalized()
    helper = Vector((1, 0, 0)) if abs(axis.x) < 0.9 else Vector((0, 1, 0))
    u = axis.cross(helper).normalized()
    v = axis.cross(u).normalized()
    return axis, u, v


def loft(rings, segments=24, cap=True):
    """Liga anéis [(centro, raio_u, raio_v, u, v)] em ordem; fecha as pontas."""
    verts, faces = [], []
    for center, ru, rv, u, v in rings:
        center = Vector(center)
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            verts.append(tuple(center + Vector(u) * (ru * math.cos(angle)) + Vector(v) * (rv * math.sin(angle))))
    for ring in range(len(rings) - 1):
        for i in range(segments):
            j = (i + 1) % segments
            a = ring * segments
            faces.append((a + i, a + j, a + segments + j, a + segments + i))
    if cap:
        faces.append(tuple(range(segments - 1, -1, -1)))
        last = (len(rings) - 1) * segments
        faces.append(tuple(last + i for i in range(segments)))
    return verts, faces


def z_loft(profile, segments=32, center=(0, 0), squash=None):
    """Loft vertical: profile = [(z, rx, ry[, y_offset])]."""
    rings = []
    for item in profile:
        z, rx, ry = item[:3]
        y = item[3] if len(item) > 3 else 0.0
        rings.append(((center[0], center[1] + y, z), rx, ry, (1, 0, 0), (0, 1, 0)))
    return loft(rings, segments)


def ellipsoid(center, radii, rotation=None, rings=14, segments=24):
    """Elipsoide; ``rotation`` é um Quaternion aplicado antes da translação."""
    center = Vector(center)
    verts = []
    faces = []
    for r in range(1, rings):
        theta = math.pi * r / rings
        for s in range(segments):
            phi = 2 * math.pi * s / segments
            point = Vector((
                radii[0] * math.sin(theta) * math.cos(phi),
                radii[1] * math.sin(theta) * math.sin(phi),
                radii[2] * math.cos(theta),
            ))
            if rotation is not None:
                point = rotation @ point
            verts.append(tuple(center + point))
    top = Vector((0, 0, radii[2]))
    bottom = Vector((0, 0, -radii[2]))
    if rotation is not None:
        top = rotation @ top
        bottom = rotation @ bottom
    verts.append(tuple(center + top))
    verts.append(tuple(center + bottom))
    top_i, bottom_i = len(verts) - 2, len(verts) - 1
    for r in range(rings - 2):
        for s in range(segments):
            t = (s + 1) % segments
            a = r * segments
            faces.append((a + s, a + t, a + segments + t, a + segments + s))
    for s in range(segments):
        t = (s + 1) % segments
        faces.append((top_i, t, s))
        last = (rings - 2) * segments
        faces.append((bottom_i, last + s, last + t))
    return verts, faces


def capsule(p0, p1, r0, r1, segments=20, steps=5):
    """Cápsula afilada: tronco de cone com semiesferas nas pontas."""
    p0, p1 = Vector(p0), Vector(p1)
    axis, u, v = _frame(p1 - p0)
    rings = []
    for i in range(steps, 0, -1):
        a = (math.pi / 2) * i / (steps + 1)
        rings.append((p0 - axis * (r0 * math.sin(a)), r0 * math.cos(a), r0 * math.cos(a), u, v))
    rings.append((p0, r0, r0, u, v))
    rings.append((p1, r1, r1, u, v))
    for i in range(1, steps + 1):
        a = (math.pi / 2) * i / (steps + 1)
        rings.append((p1 + axis * (r1 * math.sin(a)), r1 * math.cos(a), r1 * math.cos(a), u, v))
    return loft(rings, segments)


def tube(points, radii, segments=14):
    """Tubo por polilinha com raio variável; pontas fechadas."""
    rings = []
    points = [Vector(p) for p in points]
    for i, point in enumerate(points):
        previous = points[max(i - 1, 0)]
        following = points[min(i + 1, len(points) - 1)]
        _, u, v = _frame(following - previous)
        rings.append((point, radii[i], radii[i], u, v))
    return loft(rings, segments)


def box(center, size, rotation=None):
    cx, cy, cz = center
    sx, sy, sz = (s / 2 for s in size)
    raw = [(x, y, z) for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]
    verts = []
    for point in raw:
        p = Vector(point)
        if rotation is not None:
            p = rotation @ p
        verts.append((cx + p.x, cy + p.y, cz + p.z))
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return verts, faces
