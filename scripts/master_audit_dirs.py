"""Oito direções identificadas, mesma escala, mesmo enquadramento e mesmo fundo.

Cada célula é o quadro 128×128 original, sem recorte, ampliado 2× por vizinho mais próximo,
com o retângulo do quadro, a cruz do pivô e o rótulo da direção. A última faixa repete os
quadros em tamanho real.

Uso: python scripts/master_audit_dirs.py <slug> <saida.png> [clip] [quadro]
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

slug, out = sys.argv[1], Path(sys.argv[2])
clip = sys.argv[3] if len(sys.argv) > 3 else "idle"
index = int(sys.argv[4]) if len(sys.argv) > 4 else 0
render = max((Path("projects/default/characters") / slug / "stages/render").iterdir(), key=lambda p: p.stat().st_mtime)
manifest = json.loads((Path("exports") / slug / "manifest.json").read_text(encoding="utf-8"))
anim = next(a for a in manifest["animations"] if a["animation"] == clip)
BG, INK, GRID = (118, 150, 104), (20, 30, 20), (90, 120, 80)
Z = 2
size = Image.open(render / f"frames/{clip}/S/{clip}_S_{index:04d}.png").width
C = size * Z
sheet = Image.new("RGB", (C * 8, C + 40 + size + 12), BG)
draw = ImageDraw.Draw(sheet)
for k, d in enumerate(manifest["direction_order"]):
    im = Image.open(render / f"frames/{clip}/{d}/{clip}_{d}_{index:04d}.png").convert("RGBA")
    big = im.resize((C, C), Image.NEAREST)
    x = k * C
    sheet.paste(big, (x, 20), big)
    draw.rectangle((x, 20, x + C - 1, 20 + C - 1), outline=GRID)
    pv = anim["directions"][d]["pivot"]
    px, py = x + pv["x"] * Z, 20 + pv["y"] * Z
    draw.line((px - 6, py, px + 6, py), fill=INK)
    draw.line((px, py - 6, px, py + 6), fill=INK)
    draw.text((x + 6, 4), f"{d}  {anim['directions'][d]['heading_deg']:.0f}°", fill=INK)
    sheet.paste(im, (x + (C - size) // 2, C + 40), im)
draw.text((6, C + 24), f"{slug} {clip} quadro {index}: 2× em cima, tamanho real embaixo", fill=INK)
sheet.save(out)
print(out)
