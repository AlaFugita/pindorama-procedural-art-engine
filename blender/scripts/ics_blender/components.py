"""Geradores da biblioteca modular. Cada função devolve uma lista de partes:

{"name", "mesh": (verts, faces), "material": chave, "skin": {"rigid": osso} | {"bones": [...]},
 "remesh": tamanho_voxel|None, "outline": bool}

Coordenadas canônicas: esquerda anatômica em -X. Nada aqui conhece direções de render.
"""

import math

from mathutils import Euler, Vector

from .geometry import box, capsule, ellipsoid, merge, tube, z_loft

HEAD_CENTER_Z = 1.04
ARM_BONES = ["clavicle", "upper_arm", "forearm", "hand"]
TORSO_BONES = ["pelvis", "spine_01", "chest"]


def _part(name, mesh, material, skin, remesh=None, outline=True):
    return {"name": name, "mesh": mesh, "material": material, "skin": skin, "remesh": remesh,
            "outline": outline}


def _head_surface_y(x, z, head):
    """Y na frente da superfície da cabeça para ancorar traços do rosto."""
    rx, ry, rz = head["rx"], head["ry"], head["rz"]
    value = 1 - (x / rx) ** 2 - ((z - HEAD_CENTER_Z) / rz) ** 2
    return ry * math.sqrt(max(value, 0.02))


def body_compact(params, ctx):
    pieces = [
        z_loft([
            (.44, .05, .05), (.47, .105, .085), (.53, .125, .095), (.60, .112, .085),
            (.69, .12, .088), (.77, .125, .082), (.815, .075, .058), (.84, .05, .048), (.90, .046, .046),
        ]),
    ]
    for sign in (-1, 1):
        x = sign * .085
        hx, ax = sign * .125, sign * .235
        pieces += [
            capsule((x, 0, .50), (x, .012, .29), .062, .054),
            capsule((x, .012, .29), (x, 0, .085), .055, .042),
            ellipsoid((x, .05, .043), (.056, .105, .043)),
            capsule((hx, 0, .775), (ax, 0, .60), .05, .039),
            capsule((ax, 0, .60), (sign * .30, .02, .445), .039, .033),
            ellipsoid((sign * .316, .026, .405), (.043, .043, .052)),
        ]
    return [_part("body", merge(*pieces), "skin", {"bones": ctx["deform_bones"], "exclude": ["head"]},
                  remesh=.011)]


def head(params, ctx):
    rx, ry, rz, chin = params["rx"], params["ry"], params["rz"], params["chin"]
    cz = HEAD_CENTER_Z
    profile = []
    for i in range(1, 23):
        t = i / 23
        z = cz + rz * math.cos(math.pi * t)
        s = math.sin(math.pi * t)
        taper = 1.0 if t < .55 else 1 - (1 - chin) * ((t - .55) / .45) ** 1.5
        profile.append((z, rx * s * taper, ry * s * taper))
    pieces = [z_loft(profile, 40)]
    for sign in (-1, 1):
        pieces.append(ellipsoid((sign * (rx - .004), -.005, cz - .015), (.024, .036, .046)))
    return [_part("head", merge(*pieces), "skin", {"rigid": "head"}, remesh=.008)]


def face(params, ctx):
    head_params = ctx["head_params"]
    cz = HEAD_CENTER_Z
    parts = []
    eyes, whites, brows = [], [], []
    for sign in (-1, 1):
        x = sign * .082
        z = cz - .015
        y = _head_surface_y(x, z, head_params) - .004
        whites.append(ellipsoid((x, y, z), (.036, .012, .049), rings=10, segments=16))
        eyes.append(ellipsoid((x, y + .008, z - .004), (.025, .011, .038), rings=10, segments=16))
        tilt = Euler((0, sign * params["angry"], 0)).to_quaternion()
        by_z = z + .068
        by = _head_surface_y(x, by_z, head_params) + .001
        brows.append(ellipsoid((x, by, by_z), (.038, .009, .0095), tilt, rings=8, segments=14))
    highlights = []
    for sign in (-1, 1):
        x = sign * .082 - .009
        z = cz + .003
        y = _head_surface_y(sign * .082, z, head_params) + .01
        highlights.append(ellipsoid((x, y, z), (.0095, .005, .012), rings=6, segments=10))
    mouth_z = cz - .112
    mouth_y = _head_surface_y(0, mouth_z, head_params) * ctx["head_params"]["chin"] ** .4
    parts.append(_part("eye_white", merge(*whites), "#F4EFE6", {"rigid": "head"}, outline=False))
    parts.append(_part("eye_iris", merge(*eyes), params["eye"], {"rigid": "head"}, outline=False))
    parts.append(_part("eye_glint", merge(*highlights), "#FFFFFF", {"rigid": "head"}, outline=False))
    parts.append(_part("brows", merge(*brows), params["brow"], {"rigid": "head"}, outline=False))
    parts.append(_part("mouth", ellipsoid((0, mouth_y, mouth_z), (.026, .008, .0065), rings=8, segments=12),
                       "#6B2E26", {"rigid": "head"}, outline=False))
    return parts


def _hair_cap(ctx, back=.02, lift=.012):
    h = ctx["head_params"]
    cz = HEAD_CENTER_Z
    pieces = [
        ellipsoid((0, -back, cz + lift + .02), (h["rx"] + .012, h["ry"] + .012, h["rz"] - .005)),
        ellipsoid((0, -back - .06, cz - .04), (h["rx"] - .01, h["ry"] - .05, h["rz"] - .03)),
    ]
    # Franja: mechas frontais deixam o rosto livre abaixo da testa.
    for x, tip in ((-.13, -.02), (-.075, .025), (-.02, .05), (.04, .045), (.1, .02), (.15, -.03)):
        root_y = _head_surface_y(x * .75, cz + .14, h)
        tip_y = _head_surface_y(x, cz + .075 + tip, h) + .004
        pieces.append(tube([(x * .75, root_y - .02, cz + .17), (x, tip_y, cz + .075 + tip)], [.042, .012]))
    return pieces


def hair_long_tied(params, ctx):
    h = ctx["head_params"]
    cz = HEAD_CENTER_Z
    pieces = _hair_cap(ctx)
    tail_top = (0, -h["ry"] - .012, cz + .03)
    pieces.append(tube(
        [tail_top, (0, -h["ry"] - .05, cz - .08), (.012, -h["ry"] - .055, cz - .24),
         (.02, -h["ry"] - .04, cz - .42), (.02, -h["ry"] - .03, cz - .52)],
        [.038, .062, .058, .04, .012],
    ))
    tie = tube([(0, -h["ry"] - .03, cz + .0), (0, -h["ry"] - .045, cz - .05)], [.05, .05])
    return [
        _part("hair", merge(*pieces), "hair", {"rigid": "head"}, remesh=.009),
        _part("hair_tie", tie, "accent", {"rigid": "head"}),
    ]


def hair_short_spiky(params, ctx):
    h = ctx["head_params"]
    cz = HEAD_CENTER_Z
    pieces = _hair_cap(ctx, back=.01)
    for az, el, length in ((0, 75, .09), (60, 50, .08), (-60, 50, .08), (120, 45, .09),
                           (-120, 45, .09), (170, 40, .08), (30, 30, .05), (-30, 30, .05)):
        a, e = math.radians(az), math.radians(el)
        direction = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e) * .9, math.sin(e)))
        base = Vector((0, -.01, cz + .03)) + direction * (h["rx"] - .03)
        pieces.append(tube([tuple(base), tuple(base + direction * (length + .05))], [.052, .006]))
    return [_part("hair", merge(*pieces), "hair", {"rigid": "head"}, remesh=.008)]


def hair_bun(params, ctx):
    h = ctx["head_params"]
    cz = HEAD_CENTER_Z
    pieces = _hair_cap(ctx)
    pieces.append(ellipsoid((0, -.05, cz + h["rz"] + .055), (.082, .082, .074)))
    band = tube([(0, -.05, cz + h["rz"] + .005), (0, -.05, cz + h["rz"] + .022)], [.052, .052])
    return [
        _part("hair", merge(*pieces), "hair", {"rigid": "head"}, remesh=.009),
        _part("hair_band", band, "accent", {"rigid": "head"}),
    ]


def _skirt_rx(off, flare, t):
    return .138 + off + flare * t + .025 * t


def _skirt_ry(off, flare, t):
    return .106 + off + flare * t


def _torso_shell(params, off=.012):
    hem, flare = params["hem"], params["flare"]
    skirt = []
    top = .47
    steps = 6
    for i in range(steps):
        t = i / (steps - 1)
        z = top + (hem - top) * t
        skirt.append((z, _skirt_rx(off, flare, t), _skirt_ry(off, flare, t)))
    return [
        (.82, .07, .056), (.805, .10, .076), (.775, .128 + off, .09 + off), (.70, .124 + off, .094 + off),
        (.62, .116 + off, .09 + off), (.55, .126 + off, .098 + off), (.51, .136 + off, .102 + off),
    ] + skirt


def _boot_parts():
    parts = []
    for sign, suffix in ((-1, "l"), (1, "r")):
        x = sign * .085
        mesh = merge(capsule((x, .006, .22), (x, 0, .105), .057, .05),
                     ellipsoid((x, .05, .046), (.061, .11, .047)))
        parts.append(_part(f"boot_{suffix}", mesh, "secondary",
                           {"bones": [f"shin_{suffix}", f"foot_{suffix}", f"toe_{suffix}"]}, remesh=.009))
    return parts


def _belt(z=.525):
    return z_loft([(z + .021, .135, .106), (z + .016, .144, .115), (z - .016, .148, .117), (z - .021, .139, .108)], 32)


def _outfit_skin():
    return {"bones": ["pelvis", "spine_01", "chest", "thigh_l", "thigh_r"]}


def outfit_tunic(params, ctx):
    parts = [
        _part("tunic", z_loft(_torso_shell(params), 36), "primary", _outfit_skin()),
        _part("belt", _belt(), "secondary", {"bones": ["pelvis", "spine_01"]}),
        *_boot_parts(),
    ]
    rx, ry = _skirt_rx(.012, params["flare"], 1), _skirt_ry(.012, params["flare"], 1)
    trim = z_loft([(params["hem"] + .018, rx - .001, ry - .001), (params["hem"] + .016, rx + .004, ry + .004),
                   (params["hem"] - .012, rx + .006, ry + .006), (params["hem"] - .014, rx - .002, ry - .002)], 36)
    parts.append(_part("tunic_trim", trim, "accent", _outfit_skin(), outline=False))
    if params.get("long_sash"):
        sash = merge(box((.03, .126, .39), (.05, .012, .26)), box((-.04, .124, .41), (.042, .012, .22)))
        parts.append(_part("sash", sash, "accent", {"bones": ["pelvis", "thigh_l", "thigh_r"]}))
    return parts


def outfit_armor(params, ctx):
    parts = outfit_tunic({**params, "long_sash": False}, ctx)
    chest = z_loft([(.795, .10, .08), (.775, .142, .107), (.70, .14, .112), (.62, .128, .106), (.60, .118, .1)], 32)
    parts.append(_part("cuirass", chest, "secondary", {"bones": ["spine_01", "chest"]}))
    studs = [ellipsoid((x, .112, z), (.012, .008, .012), rings=6, segments=10)
             for x in (-.07, 0, .07) for z in (.66, .73)]
    parts.append(_part("studs", merge(*studs), "accent", {"bones": ["spine_01", "chest"]}, outline=False))
    return parts


def acc_feathers(params, ctx):
    h = ctx["head_params"]
    cz = HEAD_CENTER_Z
    x = -(h["rx"] - .01)  # lado esquerdo anatômico: assimetria proposital
    feathers = []
    for angle, length, colour in ((.25, .22, "accent"), (.55, .18, "primary"), (-.1, .17, "primary")):
        start = Vector((x, -.03, cz + .1))
        d = Vector((-math.sin(angle) * .7, -.22, math.cos(angle)))
        end = start + d.normalized() * length
        mid = start.lerp(end, .55) + Vector((-.012, 0, 0))
        feathers.append((tube([tuple(start), tuple(mid), tuple(end)], [.008, .03, .004], segments=10), colour))
    return [_part(f"feather_{i}", mesh, colour, {"rigid": "head"})
            for i, (mesh, colour) in enumerate(feathers)] + [
        _part("feather_clip", ellipsoid((x, -.03, cz + .1), (.024, .024, .024)), "secondary", {"rigid": "head"})
    ]


def acc_necklace(params, ctx):
    beads = []
    pendant = ellipsoid((0, .112, .70), (.021, .012, .03))
    for i in range(-5, 6):
        a = i / 5 * 1.25
        beads.append(ellipsoid((math.sin(a) * .1, math.cos(a) * .098, .79 - math.cos(a) ** 2 * .055),
                               (.012, .012, .012), rings=6, segments=10))
    return [
        _part("necklace_beads", merge(*beads), "#E9DFC6", {"rigid": "chest"}, outline=False),
        _part("necklace_pendant", pendant, "accent", {"rigid": "chest"}),
    ]


def acc_shoulder_guard(params, ctx):
    guard = ellipsoid((-.145, 0, .79), (.082, .082, .06), Euler((0, .55, 0)).to_quaternion())
    strap = capsule((-.09, .07, .775), (-.09, .07, .70), .012, .012)
    return [
        _part("shoulder_guard", guard, "secondary", {"rigid": "clavicle_l"}),
        _part("shoulder_strap", strap, "accent", {"rigid": "chest"}, outline=False),
    ]


def acc_pouch(params, ctx):
    pouch = ellipsoid((.155, .03, .48), (.04, .036, .05))
    return [_part("pouch", pouch, "secondary", {"rigid": "pelvis"})]


HAND_R = (.325, .03, .375)


def weapon_spear(params, ctx):
    x, y, z = HAND_R
    shaft = tube([(x, y, z - .22), (x, y, z + 1.17)], [.015, .013], segments=12)
    head_mesh = ellipsoid((x, y, z + 1.27), (.038, .016, .115))
    wrap = tube([(x, y, z + 1.13), (x, y, z + 1.2)], [.02, .02], segments=12)
    grip = tube([(x, y, z - .07), (x, y, z + .07)], [.02, .02], segments=12)
    return [
        _part("spear_shaft", shaft, "#7A5230", {"rigid": "hand_r"}),
        _part("spear_head", head_mesh, "#9FB0B3", {"rigid": "hand_r"}),
        _part("spear_wrap", wrap, "accent", {"rigid": "hand_r"}, outline=False),
        _part("spear_grip", grip, "secondary", {"rigid": "hand_r"}, outline=False),
    ]


def weapon_sword(params, ctx):
    x, y, z = HAND_R
    blade = box((x, y + .02, z + .36), (.05, .012, .62))
    tip = ellipsoid((x, y + .02, z + .67), (.025, .006, .045))
    guard = box((x, y + .02, z + .05), (.13, .03, .03))
    grip = tube([(x, y + .02, z - .08), (x, y + .02, z + .05)], [.02, .02], segments=12)
    return [
        _part("sword_blade", merge(blade, tip), "#C9D2D6", {"rigid": "hand_r"}),
        _part("sword_guard", guard, "accent", {"rigid": "hand_r"}),
        _part("sword_grip", grip, "secondary", {"rigid": "hand_r"}, outline=False),
    ]


def weapon_staff(params, ctx):
    x, y, z = HAND_R
    shaft = tube([(x, y, z - .3), (x, y, z + .3), (x + .01, y, z + .9), (x - .01, y, z + 1.08)],
                 [.02, .018, .017, .024], segments=12)
    stone = ellipsoid((x - .01, y, z + 1.17), (.07, .07, .09))
    return [
        _part("staff_shaft", shaft, "#5E4632", {"rigid": "hand_r"}),
        _part("staff_stone", stone, "accent", {"rigid": "hand_r"}),
    ]


GENERATORS = {
    name: value for name, value in globals().items()
    if callable(value) and not name.startswith("_") and name.split("_")[0]
    in {"body", "head", "face", "hair", "outfit", "acc", "weapon"}
}
