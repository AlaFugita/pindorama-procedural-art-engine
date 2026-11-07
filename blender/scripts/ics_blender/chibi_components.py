"""Peças chibi: formas redondas e simples, poucas peças, leitura a 128 px.

Direção: Mago do Pindorama (cabeça grande, corpo pequeno, capuz, cajado, bolsa). Originais.
Esquerda anatômica em -X; frente em +Y; altura de referência 1,0.
"""

import math

import numpy as np
from mathutils import Vector

from .geometry import box, capsule, ellipsoid, merge, tube, z_loft

HEAD = Vector((0, 0, .735))
RX, RY, RZ = .205, .19, .2


def _part(name, mesh, material, skin, remesh=None, outline=True):
    return {"name": name, "mesh": mesh, "material": material, "skin": skin, "remesh": remesh, "outline": outline}


def _face_y(x, z):
    value = 1 - (x / RX) ** 2 - ((z - HEAD.z) / RZ) ** 2
    return RY * math.sqrt(max(value, .02))


def chibi_body(params, ctx):
    pieces = [z_loft([(.26, .05, .05), (.29, .1, .082), (.35, .105, .082), (.42, .1, .078),
                      (.5, .112, .082), (.53, .08, .06), (.56, .05, .05), (.6, .05, .05)])]
    for k in (-1, 1):
        pieces += [
            capsule((k * .066, 0, .3), (k * .07, .008, .19), .038, .038),
            capsule((k * .07, .008, .19), (k * .07, 0, .08), .04, .042),
            capsule((k * .105, 0, .495), (k * .165, 0, .40), .05, .044),
            capsule((k * .165, 0, .40), (k * .205, .012, .31), .044, .042),
            ellipsoid((k * .218, .016, .285), (.05, .05, .056)),
        ]
    return [_part("body", merge(*pieces), "skin", {"bones": ctx["deform_bones"], "exclude": ["head"]}, remesh=.008)]


def chibi_head(params, ctx):
    head = ellipsoid(tuple(HEAD), (RX, RY, RZ), rings=24, segments=40)
    return [_part("head", head, "skin", {"rigid": "head"}, remesh=.007)]


def chibi_face(params, ctx):
    eyes, shine = [], []
    for k in (-1, 1):
        x, z = k * .085, HEAD.z - .042
        y = _face_y(x, z)
        eyes.append(ellipsoid((x, y - .003, z), (.038, .011, .05), rings=14, segments=20))
        shine.append(ellipsoid((x - .01, y + .006, z + .018), (.01, .005, .014), rings=8, segments=12))
    mouth = ellipsoid((0, _face_y(0, HEAD.z - .125) + .001, HEAD.z - .125), (.017, .006, .005), rings=8, segments=12)
    return [
        _part("eyes", merge(*eyes), params["eye"], {"rigid": "head"}, outline=False),
        _part("eye_shine", merge(*shine), "#FFFFFF", {"rigid": "head"}, outline=False),
        _part("mouth", mouth, "#B9694A", {"rigid": "head"}, outline=False),
    ]


def chibi_hair(params, ctx):
    pieces = [ellipsoid((0, -.006, HEAD.z + .035), (.222, .195, .168), rings=18, segments=32)]
    # Franja de lobos largos, repartida; o remesh funde tudo numa massa lisa.
    lobes = HAIR_STYLES[params.get("style", "bangs")]
    for x, z, sx, sz in lobes:
        pieces.append(ellipsoid((x, _face_y(x, z) - .012, z), (sx, .03, sz), rings=12, segments=16))
    return [_part("hair", merge(*pieces), params["color"], {"rigid": "head"}, remesh=.007)]


HAIR_STYLES = {
    # (x, z, largura, altura) de cada lobo da franja.
    "bangs": ((-.125, .775, .062, .085), (-.055, .79, .058, .07), (.02, .79, .058, .068),
              (.09, .78, .058, .08), (.15, .755, .05, .095), (-.178, .7, .05, .11), (.18, .69, .05, .11)),
    # Franja penteada para um lado, com mecha longa só à direita.
    "swept": ((-.14, .82, .07, .05), (-.07, .815, .075, .055), (.0, .8, .075, .065), (.07, .775, .07, .085),
              (.13, .73, .06, .11), (.175, .66, .05, .14), (-.18, .74, .04, .07)),
}


HOOD_C = Vector((0, -.01, .75))
HOOD_R = (.234, .222, .224)


def _hood_point(p):
    """Abre as abas embaixo e puxa o bico caído atrás."""
    p = p.copy()
    low = max(0.0, -p.z / HOOD_R[2])
    p.x *= 1 + .13 * low
    back = max(0.0, -p.y / HOOD_R[1])
    p.y -= .085 * back ** 2 * math.exp(-((p.z + .07) / .095) ** 2)
    return p


def _hood():
    rx, ry, rz = HOOD_R
    ax, az, oz = .192, .165, -.035
    rings, segments = 34, 56
    verts, faces, keep = [], [], []
    for r in range(rings + 1):
        theta = math.pi * r / rings
        for s in range(segments):
            phi = 2 * math.pi * s / segments
            p = Vector((rx * math.sin(theta) * math.cos(phi), ry * math.sin(theta) * math.sin(phi), rz * math.cos(theta)))
            keep.append(not (p.y > 0 and (p.x / ax) ** 2 + ((p.z - oz) / az) ** 2 < 1))
            verts.append(tuple(HOOD_C + _hood_point(p)))
    for r in range(rings):
        for s in range(segments):
            t = (s + 1) % segments
            a, b, c, d = r * segments + s, r * segments + t, (r + 1) * segments + t, (r + 1) * segments + s
            if keep[a] and keep[b] and keep[c] and keep[d]:
                faces.append((a, d, c, b))
    trim = []
    for a in np.linspace(0, 2 * math.pi, 73):
        x, z = (ax + .006) * math.cos(a), (az + .006) * math.sin(a) + oz
        y = ry * math.sqrt(max(1 - (x / rx) ** 2 - (z / rz) ** 2, .01))
        trim.append(tuple(HOOD_C + _hood_point(Vector((x, y, z)))))
    return (verts, faces), tube(trim, [.022] * len(trim), segments=12)


def chibi_robe(params, ctx):
    with_hood = params.get("hood", True)
    with_cape = params.get("cape", True)
    hood, trim = _hood()
    robe_bones = {"bones": ["pelvis", "spine_01", "chest"]}
    tunic = z_loft([(.53, .09, .07), (.5, .122, .092), (.42, .112, .09), (.34, .121, .106),
                    (.27, .162, .165), (.235, .174, .18)], 36)
    hem = z_loft([(.256, .169, .171), (.252, .179, .181), (.226, .182, .184), (.222, .17, .172)], 36)
    cape = z_loft([(.58, .07, .06), (.55, .13, .1), (.5, .168, .126), (.455, .184, .138), (.45, .172, .127)], 36)
    cape_trim = z_loft([(.47, .181, .135), (.466, .191, .145), (.442, .192, .146), (.438, .18, .134)], 36)
    belt = z_loft([(.345, .124, .098), (.34, .131, .105), (.312, .133, .107), (.307, .125, .099)], 32)
    buckle = ellipsoid((0, .112, .326), (.026, .01, .024), rings=8, segments=12)
    lapel = merge(tube([(-.06, .118, .56), (0, .142, .475)], [.014, .011], segments=8),
                  tube([(.06, .118, .56), (0, .142, .475)], [.014, .011], segments=8))
    strap = tube([(-.13, .08, .47), (-.04, .118, .42), (.08, .113, .34), (.16, .05, .3)], [.012] * 4, segments=8)
    strap_back = tube([(-.13, -.07, .47), (-.04, -.105, .42), (.08, -.105, .34), (.16, -.075, .3)], [.012] * 4, segments=8)
    shoulders = ["chest", "spine_01", "clavicle_l", "clavicle_r"]
    parts = []
    if with_hood:
        parts += [_part("hood", hood, "primary", {"rigid": "head"}),
                  _part("hood_trim", trim, "accent", {"rigid": "head"})]
    if with_cape:
        parts += [_part("cape", cape, "primary", {"bones": shoulders}),
                  _part("cape_trim", cape_trim, "accent", {"bones": shoulders}, outline=False)]
    else:
        # Colete curto sobre a túnica, no lugar da capinha.
        vest = z_loft([(.535, .1, .08), (.5, .132, .1), (.44, .125, .1), (.38, .128, .108), (.37, .12, .1)], 36)
        collar = z_loft([(.56, .07, .062), (.545, .095, .08), (.525, .1, .084)], 32)
        parts += [_part("vest", vest, "#6B4A2E", {"bones": ["chest", "spine_01"]}),
                  _part("collar", collar, "accent", {"bones": ["chest", "spine_01"]})]
    parts += [
        _part("lapel", lapel, "accent", {"bones": shoulders}, outline=False),
        _part("tunic", tunic, "primary", robe_bones),
        _part("tunic_hem", hem, "accent", robe_bones),
        _part("belt", merge(belt, buckle), "secondary", {"bones": ["pelvis", "spine_01"]}),
        _part("strap", merge(strap, strap_back), "secondary", {"bones": ["chest", "spine_01", "pelvis"]}, outline=False),
    ]
    for k, side in ((-1, "l"), (1, "r")):
        sleeve = capsule((k * .125, 0, .47), (k * .172, .003, .385), .058, .054)
        cuff = capsule((k * .168, .002, .392), (k * .178, .004, .372), .059, .059)
        boot = merge(capsule((k * .07, .004, .115), (k * .07, 0, .07), .057, .056),
                     ellipsoid((k * .07, .04, .046), (.066, .1, .046)))
        boot_cuff = capsule((k * .07, .005, .13), (k * .07, .005, .118), .063, .063)
        arm = {"bones": [f"clavicle_{side}", f"upper_arm_{side}", f"forearm_{side}"]}
        leg = {"bones": [f"shin_{side}", f"foot_{side}", f"toe_{side}"]}
        parts += [
            _part(f"sleeve_{side}", sleeve, "primary", arm),
            _part(f"sleeve_cuff_{side}", cuff, "accent", arm, outline=False),
            _part(f"boot_{side}", boot, "secondary", leg, remesh=.007),
            _part(f"boot_cuff_{side}", boot_cuff, "#A9683C", leg, outline=False),
        ]
    return parts


def chibi_bag(params, ctx):
    bag = ellipsoid((.18, -.08, .285), (.072, .08, .08))
    flap = ellipsoid((.186, -.08, .33), (.07, .074, .032))
    return [
        _part("bag", bag, "secondary", {"rigid": "pelvis"}),
        _part("bag_flap", flap, "#A9683C", {"rigid": "pelvis"}),
    ]


def chibi_book(params, ctx):
    """Grimório pendurado no quadril direito, no lugar da bolsa."""
    book = box((.17, -.05, .29), (.045, .1, .12))
    clasp = box((.195, -.05, .29), (.01, .03, .03))
    return [
        _part("book", book, "#7A2E2E", {"rigid": "pelvis"}),
        _part("book_clasp", clasp, "#D8B45A", {"rigid": "pelvis"}, outline=False),
    ]


def chibi_crystal_staff(params, ctx):
    """Cajado reto com cristal preso por garras."""
    x, y = -.222, .03
    # Mais alto que o cajado enrolado: o cristal precisa passar do capuz para ser lido.
    top = .84
    shaft = tube([(x, y, .055), (x, y, .3), (x, y, top)], [.018, .017, .02], segments=12)
    prongs = merge(*[tube([(x, y, top), (x + .032 * math.cos(a), y + .032 * math.sin(a), top + .05),
                           (x + .012 * math.cos(a), y + .012 * math.sin(a), top + .095)], [.008, .007, .004], segments=6)
                     for a in (0, 2.1, 4.2)])
    gem = ellipsoid((x, y, top + .05), (.03, .03, .048), rings=8, segments=8)
    return [
        _part("staff", merge(shaft, prongs), "#9A5A30", {"rigid": "hand_l"}),
        _part("staff_gem", gem, params.get("gem", "#6FD3E6"), {"rigid": "hand_l"}),
    ]


def chibi_staff(params, ctx):
    k, x, y = -1, -.222, .03
    shaft = tube([(x, y, .055), (x, y, .3), (x, y, .63)], [.019, .018, .017], segments=12)
    cx, cz = x + k * .07, .635
    curl = []
    for a in np.linspace(0, 2.5 * math.pi, 40):
        r = .07 - .04 * a / (2.5 * math.pi)
        curl.append((cx - k * r * math.cos(a), y, cz + r * math.sin(a)))
    head = tube(curl, list(np.linspace(.017, .012, len(curl))), segments=10)
    return [_part("staff", merge(shaft, head), "#9A5A30", {"rigid": "hand_l"})]


GENERATORS = {
    "chibi_body": chibi_body, "chibi_head": chibi_head, "chibi_face": chibi_face, "chibi_hair": chibi_hair,
    "chibi_robe": chibi_robe, "chibi_bag": chibi_bag, "chibi_staff": chibi_staff,
    "chibi_book": chibi_book, "chibi_crystal_staff": chibi_crystal_staff,
}
