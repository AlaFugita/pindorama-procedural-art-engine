"""Volumes da Rota A: escultura do corpo, cabelo, roupas e ornamentos, sem armas (D6).

As peças são construídas sobre a superfície real do corpo esculpido: anéis e painéis medem o
corpo antes de nascer, então acompanham a anatomia em vez de um raio paramétrico. Cada peça é
um objeto separado, o que mantém a personalização por camadas.
"""

import math

import bpy
import numpy as np
from mathutils import Euler, Vector

from .geometry import ellipsoid, merge, tube

# --- Escultura ---------------------------------------------------------------
# Deformações locais antes de subdividir: aplicadas também aos olhos.
FACE_WARPS = [
    {"c": "eyes", "r": .075, "scale": 1.14},
    {"c": (0, .17, .975), "r": .1, "move": (0, -.006, .012)},
    {"c": (0, .205, 1.02), "r": .055, "scale": .86},
]

BODY_BRUSHES = [
    # Rosto: sobrancelha pesada, testa, mandíbula firme, bochecha jovem.
    {"c": (.062, .165, 1.128), "r": .06, "a": .009, "mirror": True, "ell": (1.25, .9, .34)},
    {"c": (.1, .15, 1.145), "r": .05, "a": .006, "mirror": True, "ell": (1.2, .9, .4)},
    {"c": (.09, .155, 1.015), "r": .07, "a": .012, "mirror": True},
    {"c": (.095, .12, .985), "r": .055, "a": .01, "mirror": True},
    {"c": (0, .15, .945), "r": .05, "a": .002},
    {"c": (.175, -.02, 1.09), "r": .07, "a": -.02, "mirror": True, "dir": (-1, 0, 0)},
    # Dedos mais grossos: a mão da base é fina para a proporção compacta.
    {"c": (.37, .018, .29), "r": .13, "a": .0065, "mirror": True},
    {"c": (.375, .018, .25), "r": .1, "a": .004, "mirror": True},
    # Tronco e braços.
    {"c": (.1, .125, .775), "r": .095, "a": .012, "mirror": True, "ell": (1.2, .8, .75)},
    {"c": (.0, .14, .725), "r": .04, "a": -.006},
    {"c": (.225, 0, .80), "r": .085, "a": .015, "mirror": True},
    {"c": (.28, .03, .67), "r": .06, "a": .01, "mirror": True},
    {"c": (.33, .0, .47), "r": .07, "a": .01, "mirror": True},
    {"c": (.13, -.13, .78), "r": .1, "a": .012, "mirror": True},
    # Pernas: coxa e panturrilha cheias; joelho definido.
    {"c": (.105, .06, .38), "r": .095, "a": .014, "mirror": True},
    {"c": (.105, -.05, .18), "r": .075, "a": .012, "mirror": True},
    {"c": (.105, .055, .275), "r": .05, "a": .006, "mirror": True},
    {"c": (.1, -.09, .47), "r": .1, "a": .012, "mirror": True},
]


def _sign(value):
    return 1.0 if value >= 0 else -1.0


def strip(points, widths, thicks, normal_hint, sides=8):
    """Mecha/lâmina: seção elíptica achatada ao longo de um caminho, com ponta afilada."""
    points = [Vector(p) for p in points]
    rings = []
    for index, point in enumerate(points):
        previous = points[max(index - 1, 0)]
        following = points[min(index + 1, len(points) - 1)]
        tangent = (following - previous).normalized()
        hint = normal_hint(point) if callable(normal_hint) else Vector(normal_hint)
        side = tangent.cross(hint).normalized()
        normal = side.cross(tangent).normalized()
        ring = []
        for k in range(sides):
            angle = 2 * math.pi * k / sides
            ring.append(tuple(point + side * (widths[index] * math.cos(angle))
                              + normal * (thicks[index] * math.sin(angle))))
        rings.append(ring)
    verts = [v for ring in rings for v in ring]
    faces = []
    for r in range(len(rings) - 1):
        for k in range(sides):
            n = (k + 1) % sides
            faces.append((r * sides + k, r * sides + n, (r + 1) * sides + n, (r + 1) * sides + k))
    faces.append(tuple(range(sides - 1, -1, -1)))
    last = (len(rings) - 1) * sides
    faces.append(tuple(last + k for k in range(sides)))
    return verts, faces


def bezier(p0, p1, p2, count=9):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [p0.lerp(p1, t).lerp(p1.lerp(p2, t), t) for t in np.linspace(0, 1, count)]


def taper(count, base, tip_ratio=.02, belly=.35):
    """Largura ao longo da mecha: cresce até ``belly`` e afina até a ponta."""
    values = []
    for t in np.linspace(0, 1, count):
        if t < belly:
            values.append(base * (.55 + .45 * math.sin(t / belly * math.pi / 2)))
        else:
            u = (t - belly) / (1 - belly)
            values.append(base * (tip_ratio + (1 - tip_ratio) * (1 - u ** 1.6)))
    return values


HEAD_C = Vector((0, -.008, 1.115))


def _away(point):
    return (Vector(point) - HEAD_C).normalized()


def _scalp(azimuth, elevation, scale=1.0):
    """Ponto no couro cabeludo. azimute 0 = frente, cresce para a direita do personagem."""
    a, e = math.radians(azimuth), math.radians(elevation)
    return HEAD_C + Vector((.146 * math.sin(a) * math.cos(e), .172 * math.cos(a) * math.cos(e),
                            .187 * math.sin(e))) * scale


def hair_parts():
    knot = Vector((0, -.1, 1.285))
    locks = []
    # Massa com o tamanho medido da cabeça (meia largura 0,125 m + volume de cabelo).
    mass = merge(
        ellipsoid((0, -.03, 1.165), (.153, .158, .132), rings=18, segments=32),
        ellipsoid((0, -.095, 1.095), (.14, .082, .125), rings=14, segments=28),
        ellipsoid((0, .075, 1.225), (.105, .07, .055), rings=12, segments=20),
        ellipsoid(tuple(knot), (.056, .056, .046), rings=12, segments=20),
    )
    # Mechas finas puxadas ao coque: desenham a direção do cabelo sobre a massa.
    for azimuth in range(-170, 180, 20):
        elevation = 40 if abs(azimuth) < 70 else 10
        start = _scalp(azimuth, elevation, 1.0)
        mid = start.lerp(knot, .5) + _away(start.lerp(knot, .5)) * .02
        end = knot + (start - knot).normalized() * .025
        points = bezier(start, mid, end, 9)
        locks.append(strip(points, taper(9, .034, .35, .3), taper(9, .012, .4, .3), _away, sides=8))
    # Franja: mechas estreitas abrindo do centro, sem encobrir a sobrancelha.
    for azimuth in range(-66, 67, 11):
        if azimuth == 0:
            continue
        side = 1 if azimuth > 0 else -1
        root = _scalp(azimuth, 50 - abs(azimuth) * .28, 1.0)
        outward = _away(root)
        length = .075 + abs(azimuth) * .0009
        tip = root + Vector((side * .05, 0, -length)) + outward * .03
        mid = root + outward * .028 + Vector((side * .025, 0, -length * .35))
        points = bezier(root, mid, tip, 9)
        locks.append(strip(points, taper(9, .026, .03, .3), taper(9, .012, .1, .3), _away, sides=8))
    # Costeletas e mechas laterais.
    for azimuth, length in ((-80, .15), (80, .15), (-96, .17), (96, .17), (-112, .16), (112, .16), (-128, .15), (128, .15)):
        root = _scalp(azimuth, 12, 1.0)
        outward = _away(root)
        side = 1 if azimuth > 0 else -1
        tip = root + Vector((side * .012, 0, -length)) + outward * .022
        mid = root + outward * .024 + Vector((0, 0, -length * .4))
        points = bezier(root, mid, tip, 9)
        locks.append(strip(points, taper(9, .03, .03, .3), taper(9, .013, .1, .3), _away, sides=8))
    # Pluma do rabo de cavalo.
    for azimuth, rise, length, width in (
        (-52, .35, .17, .034), (-18, .55, .18, .036), (18, .55, .18, .036), (52, .35, .17, .034),
        (-82, .02, .2, .04), (80, .02, .2, .04), (-36, -.18, .24, .046), (34, -.18, .24, .046),
        (-14, -.3, .26, .046), (14, -.3, .26, .046), (0, -.42, .28, .05),
    ):
        a = math.radians(azimuth)
        direction = Vector((math.sin(a) * .7, -math.cos(a) * .45 - .4, rise)).normalized()
        root = knot + direction * .01
        mid = root + direction * length * .55 + Vector((0, 0, .025))
        tip = root + direction * length + Vector((0, 0, -.075))
        points = bezier(root, mid, tip, 10)
        locks.append(strip(points, taper(10, width, .03, .3), taper(10, .02, .1, .3), (0, 0, 1), sides=8))
    wrap = tube([(0, -.066, 1.262), (0, -.13, 1.31)], [.046, .042], segments=18)
    bead = ellipsoid((0, -.1, 1.293), (.034, .034, .03))
    return [("hair_mass", mass), ("hair", merge(*locks)), ("hair_tie", merge(wrap, bead))]


def feather_mesh(root, tip, width, normal, bend=.0):
    """Pena: raque central e lâmina com recortes, sem textura para disfarçar."""
    root, tip = Vector(root), Vector(tip)
    axis = tip - root
    side = axis.cross(Vector(normal)).normalized()
    up = side.cross(axis).normalized()
    rows, cols = 14, 5
    verts = []
    for r in range(rows):
        t = r / (rows - 1)
        half = width * (math.sin(math.pi * min(t * 1.05, 1) ** .7) ** .8) * (.28 if t < .12 else 1)
        notch = .78 if r in (5, 9) else 1.0
        center = root + axis * t + up * (bend * math.sin(math.pi * t) * axis.length)
        for c in range(cols):
            u = c / (cols - 1) * 2 - 1
            lift = (1 - abs(u)) * .006 - abs(u) * .004
            verts.append(tuple(center + side * (u * half * notch) + up * lift))
        for c in range(cols):
            u = c / (cols - 1) * 2 - 1
            verts.append(tuple(center + side * (u * half * notch) - up * .003))
    faces = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            a = r * 2 * cols + c
            faces.append((a, a + 1, a + 1 + 2 * cols, a + 2 * cols))
            b = a + cols
            faces.append((b, b + 2 * cols, b + 1 + 2 * cols, b + 1))
    for r in range(rows - 1):
        for edge, flip in ((0, True), (cols - 1, False)):
            a, b = r * 2 * cols + edge, (r + 1) * 2 * cols + edge
            face = (a, b, b + cols, a + cols)
            faces.append(face if flip else face[::-1])
    return verts, faces


def crown_feathers():
    knot = Vector((0, -.125, 1.30))
    meshes = []
    for azimuth, lift, length, width in (
        (-34, .95, .24, .034), (4, 1.1, .27, .038), (38, .8, .23, .034), (-70, .42, .2, .03),
        (72, .36, .19, .028),
    ):
        a = math.radians(azimuth)
        direction = Vector((math.sin(a) * .9, -.5 - .3 * math.cos(a), lift)).normalized()
        normal = Vector((math.sin(a) * .55, math.cos(a) * .3 + .75, .15))
        meshes.append(feather_mesh(knot, knot + direction * length, width, normal, .16))
    return [("crown_feathers", merge(*meshes))]


# --- Medir o corpo ------------------------------------------------------------
class Body:
    def __init__(self, co):
        self.co = co

    def ring(self, a, b, t, mask_radius, offset, sides=40, band=.012):
        """Anel perpendicular ao eixo a→b, seguindo o perfil polar real do corpo."""
        a, b = np.array(a, float), np.array(b, float)
        axis = (b - a) / np.linalg.norm(b - a)
        center = a + (b - a) * t
        helper = np.array([1.0, 0, 0]) if abs(axis[0]) < .9 else np.array([0, 1.0, 0])
        u = np.cross(axis, helper)
        u /= np.linalg.norm(u)
        v = np.cross(axis, u)
        relative = self.co - center
        along = relative @ axis
        planar = relative - along[:, None] * axis
        radial = np.linalg.norm(planar, axis=1)
        chosen = (np.abs(along) < band) & (radial < mask_radius)
        if chosen.sum() < 8:
            raise RuntimeError(f"anel sem vértices em {center}")
        px, py = planar[chosen] @ u, planar[chosen] @ v
        angle = np.arctan2(py, px)
        length = np.hypot(px, py)
        samples = np.zeros(sides)
        for k in range(sides):
            target = -math.pi + 2 * math.pi * k / sides
            delta = np.abs((angle - target + math.pi) % (2 * math.pi) - math.pi)
            near = length[delta < .3]
            samples[k] = near.max() if len(near) else length.max()
        smooth = np.convolve(np.r_[samples[-2:], samples, samples[:2]], np.ones(5) / 5, "valid")
        ring = []
        for k in range(sides):
            target = -math.pi + 2 * math.pi * k / sides
            radius = smooth[k] + offset
            ring.append(tuple(center + (u * math.cos(target) + v * math.sin(target)) * radius))
        return ring

    def sleeve(self, a, b, levels, mask_radius, sides=40):
        """Casca sobre o corpo. levels = [(t, offset)]."""
        rings = [self.ring(a, b, t, mask_radius, off, sides) for t, off in levels]
        verts = [p for ring in rings for p in ring]
        faces = []
        for r in range(len(rings) - 1):
            for k in range(sides):
                n = (k + 1) % sides
                faces.append((r * sides + k, r * sides + n, (r + 1) * sides + n, (r + 1) * sides + k))
        return verts, faces

    def front_y(self, x, z, radius=.022, sign=1.0, x_limit=.27):
        """Face do corpo em (x, z), olhando para frente (sign=1) ou para trás (sign=-1)."""
        d = np.hypot(self.co[:, 0] - x, self.co[:, 2] - z)
        near = self.co[(d < radius) & (np.abs(self.co[:, 0]) < x_limit)]
        if not len(near):
            return None
        return float((near[:, 1] * sign).max() * sign)


def panel(body, x0, x1, top, bottom, offset, hem, columns=16, rows=10, thickness=.006, sign=1.0,
          wrap=0.0):
    """Painel de tecido caindo sobre o corpo; ``hem(u)`` recorta a barra."""
    front, back = [], []
    clearance = np.zeros(columns)
    for c, u in enumerate(np.linspace(0, 1, columns)):
        x = x0 + (x1 - x0) * u
        values = [body.front_y(x, top + (bottom - top) * t, sign=sign) for t in np.linspace(0, 1, 7)]
        values = [v * sign for v in values if v is not None]
        clearance[c] = max(values) if values else .1
    clearance = np.convolve(np.r_[clearance[0], clearance, clearance[-1]], np.ones(3) / 3, "valid")
    for r, t in enumerate(np.linspace(0, 1, rows)):
        for c, u in enumerate(np.linspace(0, 1, columns)):
            x = x0 + (x1 - x0) * u
            limit = top + (bottom - top) * (t * (1 - hem(u)) + 0 * t)
            sag = math.sin(u * math.pi) * .004
            y = (clearance[c] + offset + sag + wrap * (u - .5) ** 2 * -1 + .012 * t) * sign
            front.append((x, y, limit))
            back.append((x, y - thickness * sign, limit))
    verts = front + back
    faces = []
    n = columns
    half = len(front)
    for r in range(rows - 1):
        for c in range(columns - 1):
            a = r * n + c
            quad = (a, a + 1, a + 1 + n, a + n)
            faces.append(quad[::-1] if sign > 0 else quad)
            quad2 = tuple(i + half for i in quad)
            faces.append(quad2 if sign > 0 else quad2[::-1])
    for c in range(columns - 1):
        for row in (0, rows - 1):
            a = row * n + c
            q = (a, a + 1, a + 1 + half, a + half)
            faces.append(q if (row == 0) == (sign > 0) else q[::-1])
    for r in range(rows - 1):
        for col in (0, columns - 1):
            a = r * n + col
            q = (a, a + n, a + n + half, a + half)
            faces.append(q if (col == 0) == (sign > 0) else q[::-1])
    return verts, faces


def zigzag(teeth, depth, seed=0.0):
    def hem(u):
        phase = (u * teeth + seed) % 1
        tri = 2 * abs(phase - .5)
        vary = .55 + .45 * math.sin(u * 17 + seed * 9) ** 2
        return depth * tri * vary
    return hem


def _ring_band(body, a, b, center, width, mask, offset):
    return body.sleeve(a, b, [(center - width, offset * .4), (center - width * .7, offset),
                              (center + width * .7, offset), (center + width, offset * .4)], mask)


def clothing(body):
    parts = []
    waist_a, waist_b = (0, 0, .45), (0, 0, .70)
    parts.append(("belt", merge(
        body.sleeve(waist_a, waist_b, [(.36, .004), (.385, .017), (.45, .017), (.475, .004)], .23),
    )))
    parts.append(("waist_cloth", body.sleeve(waist_a, waist_b, [(.46, .003), (.49, .01), (.57, .009), (.60, .002)], .23)))
    rope = []
    for offset, phase in ((.022, 0), (.02, 3.0)):
        ring = body.ring(waist_a, waist_b, .41 + offset * .3, .23, offset)
        path = [ring[i % len(ring)] for i in range(len(ring) + 1)]
        rope.append(tube(path, [.0085] * len(path), segments=8))
    parts.append(("belt_rope", merge(*rope)))
    front = body.front_y(0, .555) + .028
    buckle = ellipsoid((0, front, .553), (.046, .018, .046), rings=12, segments=24)
    ring_b = tube([(.046 * math.cos(a), front + .002, .553 + .046 * math.sin(a))
                   for a in np.linspace(0, 2 * math.pi, 25)], [.008] * 25, segments=8)
    parts.append(("belt_disc", merge(buckle, ring_b)))
    parts.append(("loin_cream_front", panel(body, -.165, .165, .54, .27, .018, zigzag(7, .38, .3), columns=28, rows=8, wrap=.55)))
    parts.append(("loin_red_tabard", panel(body, -.055, .055, .545, .215, .034, lambda u: .16 * abs(math.sin(u * math.pi * 3)), columns=19, rows=10, thickness=.008)))
    parts.append(("loin_back", panel(body, -.15, .15, .54, .29, .012, zigzag(6, .35, .7), columns=24, rows=8, sign=-1.0, wrap=.5)))

    for side, x in (("R", 1), ("L", -1)):
        shoulder = (x * .215, 0, .805)
        elbow = (x * .305, 0, .575)
        wrist = (x * .355, .012, .395)
        knee = (x * .105, .012, .27)
        ankle = (x * .11, 0, .08)
        parts.append((f"arm_band_{side}", _ring_band(body, shoulder, elbow, .68, .09, .1, .01)))
        parts.append((f"bracer_{side}", merge(
            body.sleeve(elbow, wrist, [(.48, .004), (.52, .012), (.98, .012), (1.02, .004)], .14),
            _ring_band(body, elbow, wrist, .56, .04, .14, .019),
            _ring_band(body, elbow, wrist, .95, .04, .14, .019),
        )))
        parts.append((f"knee_cuff_{side}", _ring_band(body, knee, ankle, .27, .1, .13, .013)))
        bands = []
        for a0, step in ((0.0, 1.0), (math.pi, 1.0), (.3, -1.0), (math.pi + .3, -1.0)):
            path, radii = [], []
            for i, t in enumerate(np.linspace(.36, .9, 18)):
                ring = body.ring(knee, ankle, t, .13, .011, sides=32)
                index = int(((a0 + step * t * 8.0) % (2 * math.pi)) / (2 * math.pi) * 32) % 32
                path.append(ring[index])
                radii.append(.015)
            bands.append(strip(path, radii, [.0055] * len(path),
                               lambda p: (Vector(p) - Vector((x * .11, 0, p[2]))).normalized()))
        parts.append((f"shin_wrap_{side}", merge(*bands)))
        sole, strap = sandal(body, x)
        parts.append((f"sandal_sole_{side}", sole))
        parts.append((f"sandal_straps_{side}", strap))
    return parts


def sandal(body, x):
    foot = body.co[(np.sign(body.co[:, 0]) == x) & (body.co[:, 2] < .075)]
    y0, y1 = foot[:, 1].min() - .012, foot[:, 1].max() + .012
    rows = 14
    ring_sides = 24
    rings_top, verts = [], []
    outline = []
    for t in np.linspace(0, 1, rows):
        y = y0 + (y1 - y0) * t
        slice_ = foot[np.abs(foot[:, 1] - y) < .018]
        if not len(slice_):
            slice_ = foot[np.argsort(np.abs(foot[:, 1] - y))[:8]]
        outline.append((y, slice_[:, 0].min() - .012, slice_[:, 0].max() + .012))
    columns = 7
    for level, z in enumerate((-.036, -.012)):
        for y, left, right in outline:
            for c in range(columns):
                verts.append((left + (right - left) * c / (columns - 1), y, z))
    faces = []
    for r in range(rows - 1):
        for c in range(columns - 1):
            a = r * columns + c
            faces.append((a, a + columns, a + columns + 1, a + 1))
            b = a + rows * columns
            faces.append((b, b + 1, b + columns + 1, b + columns))
    half = rows * columns
    for c in range(columns - 1):
        for r, flip in ((0, False), (rows - 1, True)):
            a = r * columns + c
            q = (a, a + 1, a + 1 + half, a + half)
            faces.append(q[::-1] if flip else q)
    for r in range(rows - 1):
        for c, flip in ((0, False), (columns - 1, True)):
            a = r * columns + c
            q = (a, a + half, a + half + columns, a + columns)
            faces.append(q[::-1] if flip else q)
    straps = []
    for t in (.3, .52, .75):
        y = y0 + (y1 - y0) * t
        row = foot[np.abs(foot[:, 1] - y) < .016]
        left, right = row[:, 0].min() - .004, row[:, 0].max() + .004
        top = row[:, 2].max() + .006
        cx, half = (left + right) / 2, (right - left) / 2
        path = [(cx + half * math.cos(u), y, -.012 + (top + .012) * math.sin(u))
                for u in np.linspace(0, math.pi, 13)]
        center = Vector((cx, y, 0))
        straps.append(strip(path, [.017] * 13, [.0055] * 13,
                            lambda p, center=center: (Vector(p) - center).normalized(), sides=8))
    return (verts, faces), merge(*straps)


def ornaments(body):
    parts = []
    # Colar: contas sobre o peito e cinco presas pendentes, medidos na superfície.
    beads, teeth = [], []
    for i, u in enumerate(np.linspace(-1, 1, 21)):
        x = u * .125
        z = .86 - (1 - u * u) * .082
        y = body.front_y(x, z, x_limit=.2)
        if y is None:
            continue
        size = .0165 if i % 3 else .021
        beads.append(ellipsoid((x, y + size * .8, z), (size, size * .8, size), rings=7, segments=10))
    for u, length in ((-.6, .045), (-.3, .062), (0, .078), (.3, .062), (.6, .045)):
        x = u * .125
        z = .86 - (1 - u * u) * .082 - .01
        y = body.front_y(x, z, x_limit=.2) + .018
        path = [(x, y, z), (x * 1.02, y + .008, z - length * .55), (x * 1.08, y + .002, z - length)]
        teeth.append(strip(path, [.014, .013, .001], [.009, .008, .001], (0, 1, 0), sides=8))
    parts.append(("necklace_beads", merge(*beads)))
    parts.append(("necklace_teeth", merge(*teeth)))
    # Ombreira de penas: dois leques assentados sobre deltoide e clavícula.
    feathers = []
    for x in (1, -1):
        for row, (radius, length, count, droop) in enumerate(((.14, .16, 6, .8), (.09, .13, 5, .5))):
            for i in range(count):
                u = i / (count - 1)
                a = math.radians(-70 + 140 * u)
                root = Vector((x * (.175 + .05 * math.cos(a)), .13 * math.sin(a), .835 + row * .03 - abs(u - .5) * .02))
                outward = Vector((x * math.cos(a) * .9, math.sin(a) * .85, -droop)).normalized()
                feathers.append(feather_mesh(root, root + outward * length, .04, (x * .3, 0, 1), .1))
    parts.append(("shoulder_feathers", merge(*feathers)))
    earrings = []
    for x in (1, -1):
        earrings.append(ellipsoid((x * .136, -.012, 1.0), (.0095, .0095, .016), rings=8, segments=12))
        earrings.append(ellipsoid((x * .136, -.012, .972), (.0085, .0085, .01), rings=8, segments=12))
    parts.append(("earrings", merge(*earrings)))
    return parts


VOXEL_UNION = {"hair_mass": .007}


def _voxel_union(obj, size):
    remesh = obj.modifiers.new("remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = size
    smooth = obj.modifiers.new("smooth", "SMOOTH")
    smooth.iterations = 18
    smooth.factor = .6
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()
    obj.data = mesh


def build_all(scene, skip, body_co):
    body = Body(body_co)
    groups = [hair_parts(), crown_feathers(), clothing(body), ornaments(body)]
    objects = []
    for group in groups:
        for name, (verts, faces) in group:
            if name in skip:
                continue
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(verts, [], faces)
            mesh.update()
            obj = bpy.data.objects.new(name, mesh)
            scene.collection.objects.link(obj)
            if name in VOXEL_UNION:
                _voxel_union(obj, VOXEL_UNION[name])
            obj.data.shade_smooth()
            objects.append(obj)
    return objects


__all__ = ["BODY_BRUSHES", "Euler", "build_all"]
