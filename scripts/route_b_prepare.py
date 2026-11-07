"""Entrada da Rota B: recorta o herói da prancha e gera a máscara localmente.

Não usa RMBG-1.4 (licença não comercial). A prancha tem fundo escuro uniforme, então a máscara
parte de preenchimento pelas bordas. A pluma de cabelo tem quase a cor do fundo e por isso é
protegida por contorno traçado à mão. Arco, flechas e aljava (D6) saem por um polígono que segue
a borda do corpo: cortes retos viraram placas planas na malha gerada. A imagem nunca sai daqui.

Uso: python scripts/route_b_prepare.py <referencia> <saida.png>
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

# Coordenadas da prancha (1536×1024), traçadas sobre ampliação com grade.
PROTECT = [
    # Pluma e cabelo de trás.
    [(22, 142), (60, 108), (120, 60), (180, 90), (205, 92), (230, 150), (210, 285), (170, 285),
     (152, 250), (165, 215), (140, 218), (170, 178), (150, 165), (125, 178), (95, 192), (80, 170),
     (75, 197), (58, 172), (42, 198), (40, 152)],
    # Pena escura do topo.
    [(186, 14), (215, 30), (235, 70), (215, 80), (200, 40)],
]
EQUIPMENT = [
    (0, 205), (70, 205), (92, 200), (118, 205), (138, 222), (152, 250), (165, 280), (200, 292),
    (170, 300), (143, 310), (110, 335), (96, 398), (92, 402), (110, 412), (100, 440), (86, 480), (82, 510),
    (84, 560), (88, 600), (100, 640), (115, 655), (118, 700), (110, 725), (100, 780), (0, 800),
]
# Fundo preso entre braço e cintura: retirado depois do preenchimento de furos.
GAPS = [[(168, 425), (195, 418), (198, 455), (205, 478), (196, 498), (163, 503), (158, 470)]]


def polygon_mask(size, polygons):
    canvas = Image.new("L", size, 0)
    draw = ImageDraw.Draw(canvas)
    for points in polygons:
        draw.polygon(points, fill=255)
    return np.asarray(canvas) > 0


source, output = Path(sys.argv[1]), Path(sys.argv[2])
image = Image.open(source).convert("RGB").crop((0, 0, 440, 1024))
array = np.asarray(image, dtype=float)
background = np.median(array[:40, :40].reshape(-1, 3), axis=0)
distance = np.abs(array - background).max(axis=2)
labels, _ = ndimage.label(distance < 24)
border = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
border.discard(0)
outside = np.isin(labels, list(border))

mask = ~outside | polygon_mask(image.size, PROTECT)
mask &= ~polygon_mask(image.size, [EQUIPMENT])
mask = ndimage.binary_opening(mask, iterations=2)
labels, count = ndimage.label(mask)
sizes = ndimage.sum(mask, labels, range(1, count + 1))
mask = labels == (int(np.argmax(sizes)) + 1)
mask = ndimage.binary_fill_holes(mask) & ~polygon_mask(image.size, GAPS)
alpha = ndimage.gaussian_filter(mask.astype(float), .8)

rgba = np.dstack((array, alpha * 255)).astype(np.uint8)
result = Image.fromarray(rgba, "RGBA")
result = result.crop(result.getbbox())
side = int(max(result.size) * 1.1)
canvas = Image.new("RGBA", (side, side), (255, 255, 255, 0))
canvas.paste(result, ((side - result.width) // 2, (side - result.height) // 2))
output.parent.mkdir(parents=True, exist_ok=True)
canvas.save(output)
preview = Image.new("RGB", canvas.size, (255, 255, 255))
preview.paste(canvas, (0, 0), canvas)
preview.save(output.with_name(output.stem + "_preview.png"))
print(result.size, float(mask.mean()))
