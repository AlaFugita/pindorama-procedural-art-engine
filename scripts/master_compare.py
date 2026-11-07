"""Folhas comparativas A × B nas mesmas condições.

Uso: python scripts/master_compare.py <tentativa_a> <tentativa_b>
"""

import sys

from app.core.config import ARTIFACTS_DIR, REPO_ROOT
from PIL import Image, ImageDraw

BG = (46, 48, 54, 255)
root = ARTIFACTS_DIR / "master_prototype"
a, b = root / "route_a" / sys.argv[1], root / "route_b" / sys.argv[2]
out = REPO_ROOT / "docs/audit/master_prototype"


def flat(path):
    image = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", image.size, BG)
    base.alpha_composite(image)
    return base.convert("RGB")


def table(rows, names, scale, target):
    cell = flat(rows[0][1] / f"{names[0]}.png").size
    w, h = int(cell[0] * scale), int(cell[1] * scale)
    sheet = Image.new("RGB", (w * len(names), h * len(rows)), BG[:3])
    draw = ImageDraw.Draw(sheet)
    for r, (label, folder) in enumerate(rows):
        for c, name in enumerate(names):
            sheet.paste(flat(folder / f"{name}.png").resize((w, h), Image.LANCZOS), (c * w, r * h))
        draw.text((10, r * h + 8), label, fill=(255, 255, 255))
    sheet.save(out / target)


rows = [("ROTA A (t08)", a), ("ROTA B (t03)", b)]
table(rows, ["frente", "tres_quartos", "perfil", "costas"], .62, "comparativo_quatro_vistas.png")
table(rows, ["rosto_frente", "rosto_34"], .8, "comparativo_rosto.png")

if len(sys.argv) > 3:
    c = root / "route_c" / sys.argv[3]
    rows = [("ROTA A (t08)", a), ("ROTA B (t03)", b), (f"ROTA C ({sys.argv[3]})", c)]
    table(rows, ["frente", "tres_quartos", "perfil", "costas"], .5, "comparativo_abc_quatro_vistas.png")
    table(rows, ["rosto_frente", "rosto_34"], .62, "comparativo_abc_rosto.png")
    reference = flat(root / "route_b/input/hero_rgba_v2.png").crop((340, 40, 760, 1040))
    clay = Image.open(c / "tres_quartos.png").convert("RGBA")
    crop = flat(c / "tres_quartos.png").crop(clay.getbbox())
    crop = crop.resize((crop.width * 1000 // crop.height, 1000), Image.LANCZOS)
    side = Image.new("RGB", (reference.width + crop.width + 40, 1000), BG[:3])
    side.paste(reference, (0, 0))
    side.paste(crop, (reference.width + 40, 0))
    side.save(out / "rota_c_lado_a_lado.png")

# Escala de jogo: mesma altura do sprite (cerca de 240 px) ampliada 3× sem suavizar.
sheet = Image.new("RGB", (1280, 760), BG[:3])
for index, folder in enumerate((a, b)):
    image = flat(folder / "jogo_tres_quartos.png")
    box = Image.open(folder / "jogo_tres_quartos.png").convert("RGBA").getbbox()
    crop = image.crop(box)
    small = crop.resize((crop.width * 240 // crop.height, 240), Image.LANCZOS)
    big = small.resize((small.width * 3, 720), Image.NEAREST)
    sheet.paste(big, (20 + index * 640, 20))
sheet.save(out / "comparativo_escala_jogo.png")
print("ok")
