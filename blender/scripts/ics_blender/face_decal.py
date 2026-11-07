"""Rosto como decalque vetorial procedural (estilo ilustração chibi, não realista).

As formas são desenhadas num plano do rosto (x, z em metros, x = direita anatômica) e
"embrulhadas" na superfície da cabeça. Cada traço vira um laço 3D em coordenadas de repouso;
a composição projeta o laço pela câmera em cada quadro e pinta só onde a cabeça é visível.
Assim o rosto acompanha giro e animação nas 8 direções, sem sombra nem espessura de malha.
"""

import math

from .chibi_components import HEAD, RX, RY, RZ, _face_y


def _on_head(x, z, lift=.003):
    return (x, _face_y(x, z) + lift, z)


def _ellipse(cx, cz, rx, rz, n=28, start=0.0, end=2 * math.pi):
    return [(cx + rx * math.cos(a), cz + rz * math.sin(a))
            for a in [start + (end - start) * i / (n - 1 if end - start < 2 * math.pi else n) for i in range(n)]]


def _band(points, width_at):
    """Traço com espessura variável: devolve o polígono fechado em volta da linha central."""
    left, right = [], []
    for i, (x, z) in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, len(points) - 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, tz) or 1.0
        nx, nz = -tz / length, tx / length
        w = width_at(i / max(1, len(points) - 1)) / 2
        left.append((x + nx * w, z + nz * w))
        right.append((x - nx * w, z - nz * w))
    return left + right[::-1]


def features(params):
    """Lista de traços: nome, cor (hex), opacidade, laço 3D e centro (para a visibilidade)."""
    eye_color = params.get("eye", "#2A1A14")
    iris_color = params.get("iris", "#7A4A2A")
    brow_color = params.get("brow", "#6B3A20")
    out = []

    def add(name, color, loop2d, alpha=1.0, centre=None):
        cx = sum(p[0] for p in loop2d) / len(loop2d) if centre is None else centre[0]
        cz = sum(p[1] for p in loop2d) / len(loop2d) if centre is None else centre[1]
        c = _on_head(cx, cz)
        n = ((c[0] - HEAD.x) / RX ** 2, (c[1] - HEAD.y) / RY ** 2, (c[2] - HEAD.z) / RZ ** 2)
        length = math.sqrt(sum(v * v for v in n)) or 1.0
        out.append({"name": name, "color": color, "alpha": alpha, "loop": [_on_head(x, z) for x, z in loop2d],
                    "centre": c, "normal": [v / length for v in n]})

    ez = HEAD.z - params.get("eye_drop", .048)
    for k in (-1, 1):
        ex = k * params.get("eye_spacing", .082)
        add(f"blush_{k}", "#F29A86", _ellipse(k * .128, HEAD.z - .108, .03, .016), alpha=.45)
        add(f"eye_{k}", eye_color, _ellipse(ex, ez, .031, .045))
        add(f"iris_{k}", iris_color, _ellipse(ex, ez - .014, .022, .025))
        add(f"shine_{k}", "#FFFFFF", _ellipse(ex - k * .009, ez + .016, .011, .013))
        add(f"shine2_{k}", "#FFFFFF", _ellipse(ex + k * .011, ez - .022, .005, .005, n=12))
        # Linha dos cílios: arco grosso no topo do olho, com pequena ponta para fora.
        arc = _ellipse(ex, ez + .002, .036, .05, n=20, start=math.radians(20 if k > 0 else 160),
                       end=math.radians(160 if k > 0 else 20))
        arc.append((ex + k * .046, ez + .026))
        add(f"lash_{k}", eye_color, _band(arc, lambda t: .006 + .006 * math.sin(math.pi * t)), centre=(ex, ez + .04))
        # Olho fechado (piscar): arco curvado para baixo, com cílio no canto.
        closed = [(ex - .034 + .068 * t, ez - .004 - .012 * math.sin(math.pi * t)) for t in [i / 10 for i in range(11)]]
        add(f"closed_{k}", eye_color, _band(closed, lambda t: .006 + .004 * math.sin(math.pi * t)), centre=(ex, ez))
        brow = [(ex - k * .026, ez + .086), (ex, ez + .094), (ex + k * .03, ez + .088)]
        brow = [(brow[0][0] + (brow[2][0] - brow[0][0]) * t, ez + .066 + .008 * math.sin(math.pi * t) + .003 * (1 - t))
                for t in [i / 8 for i in range(9)]]
        add(f"brow_{k}", brow_color, _band(brow, lambda t: .004 + .004 * math.sin(math.pi * t)), alpha=.9)
    mz = HEAD.z - params.get("mouth_drop", .118)
    smile = [(-.02 + .04 * t, mz - .007 * math.sin(math.pi * t)) for t in [i / 10 for i in range(11)]]
    add("mouth", params.get("mouth", "#8C3B32"), _band(smile, lambda t: .005 + .003 * math.sin(math.pi * t)))
    return out


def chibi_face_decal(params, ctx):
    """O rosto não gera malha: é desenhado na composição a partir de ``features``."""
    return []


GENERATORS = {"chibi_face_decal": chibi_face_decal}
