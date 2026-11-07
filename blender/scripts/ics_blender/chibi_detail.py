"""Peças chibi detalhadas: mesma silhueta e mesmo rig do Aprendiz, com camadas e detalhes.

Evolução de ``chibi_components`` (que continua existindo como "antes"). Cada detalhe é
geometria de verdade, para gerar sombra, linha interna e leitura de material no pixel art:
dobras deslocam a superfície; costuras, anéis e laços são peças finas com papel próprio.
"""

import math

import numpy as np
from mathutils import Vector

from .chibi_components import HEAD, HOOD_C, HOOD_R, RX, _face_y, _hood_point, _part
from .geometry import box, capsule, ellipsoid, merge, tube
from .master_costume import strip


def fold_loft(profile, folds, amplitude, segments=48, phase=0.0, front_flat=0.0):
    """Loft vertical com dobras: profile = [(z, rx, ry)], amplitude(z) em fração do raio.

    ``front_flat`` reduz as dobras na frente (onde o tecido fica esticado sobre o corpo).
    """
    verts, faces = [], []
    for z, rx, ry in profile:
        a = amplitude(z)
        for i in range(segments):
            t = 2 * math.pi * i / segments
            front = max(0.0, math.sin(t))
            k = 1 + a * math.cos(folds * t + phase) * (1 - front_flat * front)
            verts.append((rx * k * math.cos(t), ry * k * math.sin(t), z))
    for r in range(len(profile) - 1):
        for i in range(segments):
            j = (i + 1) % segments
            a = r * segments
            faces.append((a + i, a + j, a + segments + j, a + segments + i))
    faces.append(tuple(range(segments - 1, -1, -1)))
    last = (len(profile) - 1) * segments
    faces.append(tuple(last + i for i in range(segments)))
    return verts, faces


def _ring(z, rx, ry, segments=40, y=0.0):
    return [(rx * math.cos(t), y + ry * math.sin(t), z) for t in np.linspace(0, 2 * math.pi, segments + 1)]


# ---------------------------------------------------------------- rosto

def chibi_face_detail(params, ctx):
    whites, irises, pupils, shines, lids, brows, blush = [], [], [], [], [], [], []
    for k in (-1, 1):
        x, z = k * .084, HEAD.z - .045
        y = _face_y(x, z)
        whites.append(ellipsoid((x, y - .006, z), (.036, .012, .05), rings=12, segments=18))
        irises.append(ellipsoid((x + k * .004, y - .001, z - .004), (.027, .01, .041), rings=12, segments=18))
        pupils.append(ellipsoid((x + k * .005, y + .003, z - .008), (.014, .007, .022), rings=8, segments=12))
        shines.append(ellipsoid((x - .009, y + .007, z + .016), (.009, .004, .012), rings=6, segments=10))
        shines.append(ellipsoid((x + .01, y + .006, z - .024), (.005, .003, .006), rings=6, segments=8))
        # Pálpebra superior grossa, mais pesada no canto de fora (traço de anime/chibi).
        lid = [(x - k * .036, _face_y(x - k * .036, z + .03) + .002, z + .03),
               (x, _face_y(x, z + .05) + .004, z + .052),
               (x + k * .04, _face_y(x + k * .04, z + .036) + .002, z + .03)]
        lids.append(tube(lid, [.006, .009, .011], segments=8))
        bz = z + .088
        brow = [(x - k * .032, _face_y(x - k * .032, bz + .002) + .002, bz + .002),
                (x + k * .002, _face_y(x, bz + .01) + .003, bz + .01),
                (x + k * .036, _face_y(x + k * .036, bz - .008) + .002, bz - .008)]
        brows.append(tube(brow, [.006, .008, .005], segments=6))
        cx, cz = k * .118, HEAD.z - .1
        blush.append(ellipsoid((cx, _face_y(cx, cz) - .004, cz), (.026, .008, .014), rings=8, segments=12))
    nz = HEAD.z - .095
    nose = ellipsoid((0, _face_y(0, nz) + .004, nz), (.012, .01, .01), rings=8, segments=12)
    mz = HEAD.z - .135
    smile = [(x, _face_y(x, mz + abs(x) * .6) + .002, mz + (x / .024) ** 2 * .006) for x in np.linspace(-.024, .024, 7)]
    mouth = tube(smile, [.004] * 7, segments=6)
    head = {"rigid": "head"}
    return [
        _part("eye_white", merge(*whites), "#FBF4EA", head, outline=False),
        _part("iris", merge(*irises), params.get("eye", "#5A3420"), head, outline=False),
        _part("eyes", merge(*pupils), "#1E1210", head, outline=False),
        _part("eye_shine", merge(*shines), "#FFFFFF", head, outline=False),
        _part("lashes", merge(*lids), "#2A1712", head, outline=False),
        _part("brows", merge(*brows), params.get("brow", "#7A4326"), head, outline=False),
        _part("blush", merge(*blush), "#F2A08A", head, outline=False),
        _part("nose", nose, "skin", head, outline=False),
        _part("mouth", mouth, "#9C4A3A", head, outline=False),
    ]


# ---------------------------------------------------------------- cabelo

def chibi_hair_detail(params, ctx):
    color = params["color"]
    cap = ellipsoid((0, -.006, HEAD.z + .035), (.214, .19, .165), rings=18, segments=32)

    def out(p):
        return (Vector(p) - HEAD).normalized()

    locks = []
    # Franja: mechas afiladas que nascem sob a borda do capuz e terminam em ponta.
    for x0, z0, length, bend in ((-.15, .88, .13, -.02), (-.095, .9, .12, -.012), (-.035, .905, .105, .006),
                                 (.03, .905, .11, .014), (.09, .895, .125, .02), (.145, .875, .14, .026)):
        x1, z1 = x0 + bend, z0 - length
        mx, mz = (x0 + x1) / 2 + bend * .6, (z0 + z1) / 2
        pts = [(x, _face_y(x, z) - .004 + .016 * math.sin(math.pi * t), z)
               for t, (x, z) in zip(np.linspace(0, 1, 7),
                                    [(x0 + (x1 - x0) * u + (mx - (x0 + x1) / 2) * math.sin(math.pi * u), z0 + (z1 - z0) * u)
                                     for u in np.linspace(0, 1, 7)])]
        widths = [.03, .034, .032, .026, .018, .009, .002]
        locks.append(strip(pts, widths, [.012, .014, .013, .011, .008, .005, .002], out, sides=8))
    # Mechas laterais longas, na frente das orelhas.
    for k in (-1, 1):
        pts = [(k * (RX - .02), .02, .8), (k * (RX - .005), .045, .72), (k * (RX - .012), .06, .64), (k * (RX - .03), .065, .59)]
        locks.append(strip(pts, [.03, .034, .026, .004], [.016, .016, .012, .003], out, sides=8))
    return [
        _part("hair", cap, color, {"rigid": "head"}, remesh=.007),
        _part("hair_locks", merge(*locks), color, {"rigid": "head"}),
    ]


# ---------------------------------------------------------------- roupa

def _hood_detail(folds=7, amp=.085):
    """Capuz do Aprendiz com dobras caindo para trás e para baixo."""
    rx, ry, rz = HOOD_R
    ax, az, oz = .192, .165, -.035
    rings, segments = 40, 72
    verts, faces, keep = [], [], []
    for r in range(rings + 1):
        theta = math.pi * r / rings
        for s in range(segments):
            phi = 2 * math.pi * s / segments
            p = Vector((rx * math.sin(theta) * math.cos(phi), ry * math.sin(theta) * math.sin(phi), rz * math.cos(theta)))
            keep.append(not (p.y > 0 and (p.x / ax) ** 2 + ((p.z - oz) / az) ** 2 < 1))
            low = max(0.0, -p.z / rz) ** 1.2
            back = max(0.0, -p.y / ry)
            fold = 1 + amp * low * (.4 + .6 * back) * math.cos(folds * phi)
            q = _hood_point(Vector((p.x * fold, p.y * fold, p.z)))
            verts.append(tuple(HOOD_C + q))
    for r in range(rings):
        for s in range(segments):
            t = (s + 1) % segments
            a, b, c, d = r * segments + s, r * segments + t, (r + 1) * segments + t, (r + 1) * segments + s
            if keep[a] and keep[b] and keep[c] and keep[d]:
                faces.append((a, d, c, b))
    trim = []
    for a in np.linspace(0, 2 * math.pi, 97):
        x, z = (ax + .006) * math.cos(a), (az + .006) * math.sin(a) + oz
        y = ry * math.sqrt(max(1 - (x / rx) ** 2 - (z / rz) ** 2, .01))
        trim.append(tuple(HOOD_C + _hood_point(Vector((x, y, z)))))
    # Costura central: da testa ao bico, por cima.
    seam = []
    for u in np.linspace(.15, 2.3, 22):
        p = Vector((0, -ry * math.sin(u), rz * math.cos(u)))
        seam.append(tuple(HOOD_C + _hood_point(p) * 1.012))
    return (verts, faces), tube(trim, [.022] * len(trim), segments=12), tube(seam, [.0045] * len(seam), segments=6)


def chibi_robe_detail(params, ctx):
    hood, trim, seam = _hood_detail()
    shoulders = ["chest", "spine_01", "clavicle_l", "clavicle_r"]
    robe = {"bones": ["pelvis", "spine_01", "chest"]}
    # Capinha com dobras que abrem para a barra; frente mais lisa.
    cape = fold_loft([(.58, .07, .06), (.55, .13, .1), (.5, .168, .126), (.455, .186, .14), (.44, .18, .134)],
                     folds=9, amplitude=lambda z: max(0.0, (.56 - z) / .12) * .12, front_flat=.5)
    cape_trim = fold_loft([(.452, .186, .142), (.446, .196, .151), (.43, .197, .152), (.425, .186, .141)],
                          folds=9, amplitude=lambda z: .12, front_flat=.5)
    tunic = fold_loft([(.53, .09, .07), (.5, .122, .092), (.42, .112, .09), (.34, .121, .106),
                       (.27, .162, .165), (.235, .174, .18)],
                      folds=10, amplitude=lambda z: max(0.0, (.34 - z) / .1) * .09, front_flat=.3)
    hem = fold_loft([(.256, .169, .171), (.252, .179, .181), (.226, .182, .184), (.222, .17, .172)],
                    folds=10, amplitude=lambda z: .09, front_flat=.3)
    belt = fold_loft([(.345, .124, .098), (.34, .131, .105), (.312, .133, .107), (.307, .125, .099)],
                     folds=1, amplitude=lambda z: 0.0)
    buckle = merge(box((0, .118, .326), (.05, .012, .042)), box((0, .126, .326), (.026, .008, .022)))
    pouch = merge(ellipsoid((-.085, .1, .3), (.035, .028, .036)), ellipsoid((-.085, .112, .322), (.034, .02, .014)))
    lapel = merge(tube([(-.06, .118, .56), (0, .142, .475)], [.014, .011], segments=8),
                  tube([(.06, .118, .56), (0, .142, .475)], [.014, .011], segments=8))
    emblem = merge(ellipsoid((0, .146, .5), (.024, .01, .024), rings=8, segments=14),
                   ellipsoid((0, .153, .5), (.011, .006, .011), rings=6, segments=10))
    strap = tube([(-.13, .08, .47), (-.04, .118, .42), (.08, .113, .34), (.16, .05, .3)], [.012] * 4, segments=8)
    strap_back = tube([(-.13, -.07, .47), (-.04, -.105, .42), (.08, -.105, .34), (.16, -.075, .3)], [.012] * 4, segments=8)
    parts = [
        _part("hood", hood, "primary", {"rigid": "head"}),
        _part("hood_trim", trim, "accent", {"rigid": "head"}),
        _part("hood_seam", seam, "accent", {"rigid": "head"}, outline=False),
        _part("cape", cape, "primary", {"bones": shoulders}),
        _part("cape_trim", cape_trim, "accent", {"bones": shoulders}, outline=False),
        _part("lapel", lapel, "accent", {"bones": shoulders}, outline=False),
        _part("emblem", emblem, "#D9B35B", {"bones": ["chest"]}, outline=False),
        _part("tunic", tunic, "primary", robe),
        _part("tunic_hem", hem, "accent", robe),
        _part("belt", belt, "secondary", {"bones": ["pelvis", "spine_01"]}),
        _part("buckle", buckle, "#D9B35B", {"bones": ["pelvis", "spine_01"]}, outline=False),
        _part("pouch", pouch, "#8A5230", {"rigid": "pelvis"}),
        _part("strap", merge(strap, strap_back), "secondary", {"bones": ["chest", "spine_01", "pelvis"]}, outline=False),
    ]
    for k, side in ((-1, "l"), (1, "r")):
        arm = {"bones": [f"clavicle_{side}", f"upper_arm_{side}", f"forearm_{side}"]}
        leg = {"bones": [f"shin_{side}", f"foot_{side}", f"toe_{side}"]}
        sleeve = capsule((k * .125, 0, .47), (k * .172, .003, .385), .058, .054)
        cuff = capsule((k * .168, .002, .394), (k * .178, .004, .37), .061, .06)
        bracer = capsule((k * .18, .005, .36), (k * .197, .01, .318), .047, .045)
        wraps = merge(*[tube(_ring(z, .049, .048, 20), [.004] * 21, segments=5) for z in (.35, .335, .32)])
        wraps = ([(v[0] + k * (.18 + (.36 - v[2]) * .4), v[1] + .006, v[2]) for v in wraps[0]], wraps[1])
        boot = merge(capsule((k * .07, .004, .118), (k * .07, 0, .07), .057, .056),
                     ellipsoid((k * .07, .042, .05), (.064, .098, .044)))
        sole = ellipsoid((k * .07, .04, .0145), (.068, .104, .014))
        toe = ellipsoid((k * .07, .1, .042), (.045, .04, .03))
        boot_cuff = fold_loft([(.148, .066, .066), (.135, .07, .07), (.118, .066, .066)], folds=6,
                              amplitude=lambda z: .06)
        boot_cuff = ([(v[0] + k * .07, v[1] + .005, v[2]) for v in boot_cuff[0]], boot_cuff[1])
        laces = merge(*[tube([(k * .07 - .02, .062 + i * .01, .1 - i * .015), (k * .07 + .02, .066 + i * .01, .092 - i * .015)],
                             [.004, .004], segments=5) for i in range(3)])
        parts += [
            _part(f"sleeve_{side}", sleeve, "primary", arm),
            _part(f"sleeve_cuff_{side}", cuff, "accent", arm, outline=False),
            _part(f"bracer_{side}", bracer, "#8A5230", arm),
            _part(f"lace_bracer_{side}", wraps, "#5A3420", arm, outline=False),
            _part(f"boot_{side}", boot, "secondary", leg, remesh=.006),
            _part(f"boot_sole_{side}", sole, "#4A2C1C", leg),
            _part(f"boot_toe_{side}", toe, "secondary", leg, outline=False),
            _part(f"boot_cuff_{side}", boot_cuff, "#A9683C", leg, outline=False),
            _part(f"lace_{side}", laces, "#5A3420", leg, outline=False),
        ]
    return parts


# ---------------------------------------------------------------- bolsa e cajado

def chibi_bag_detail(params, ctx):
    bag = ellipsoid((.18, -.08, .285), (.072, .08, .08))
    flap = ellipsoid((.186, -.08, .33), (.07, .074, .032))
    clasp = box((.235, -.08, .312), (.012, .026, .03))
    charm = merge(tube([(.24, -.06, .3), (.25, -.055, .26)], [.003, .003], segments=5),
                  ellipsoid((.25, -.055, .25), (.012, .012, .014), rings=6, segments=8))
    return [
        _part("bag", bag, "secondary", {"rigid": "pelvis"}),
        _part("bag_flap", flap, "#A9683C", {"rigid": "pelvis"}),
        _part("clasp", clasp, "#D9B35B", {"rigid": "pelvis"}, outline=False),
        _part("bell", charm, "#D9B35B", {"rigid": "pelvis"}, outline=False),
    ]


def chibi_staff_detail(params, ctx):
    k, x, y = -1, -.222, .03
    shaft = tube([(x, y, .055), (x + .003, y, .2), (x - .002, y, .4), (x, y, .63)], [.019, .018, .018, .017], segments=12)
    cx, cz = x + k * .07, .635
    curl = []
    for a in np.linspace(0, 2.5 * math.pi, 48):
        r = .07 - .04 * a / (2.5 * math.pi)
        curl.append((cx - k * r * math.cos(a), y, cz + r * math.sin(a)))
    head = tube(curl, list(np.linspace(.018, .011, len(curl))), segments=10)
    wrap = merge(*[tube(_ring(z, .023, .023, 16, y), [.005] * 17, segments=5) for z in np.linspace(.25, .31, 4)])
    wrap = ([(v[0] + x, v[1], v[2]) for v in wrap[0]], wrap[1])
    rings = merge(*[tube(_ring(z, .022, .022, 16, y), [.006] * 17, segments=5) for z in (.45, .6)])
    rings = ([(v[0] + x, v[1], v[2]) for v in rings[0]], rings[1])
    orb = ellipsoid((cx - k * .006, y, cz + .006), (.026, .026, .026), rings=10, segments=14)
    return [
        _part("staff", merge(shaft, head), "#9A5A30", {"rigid": "hand_l"}),
        _part("wrap", wrap, "#EFDFB8", {"rigid": "hand_l"}, outline=False),
        _part("stud", rings, "#D9B35B", {"rigid": "hand_l"}, outline=False),
        _part("orb", orb, params.get("glow", "#FFD45A"), {"rigid": "hand_l"}),
    ]


GENERATORS = {
    "chibi_face_detail": chibi_face_detail, "chibi_hair_detail": chibi_hair_detail,
    "chibi_robe_detail": chibi_robe_detail, "chibi_bag_detail": chibi_bag_detail,
    "chibi_staff_detail": chibi_staff_detail,
}
