"""Antes/depois em matriz 2×2: geometria (protótipo × detalhada) × acabamento (suave × pixel).

Separa o que veio da modelagem e o que veio do acabamento. Vistas frontal (S), três quartos
(SE) e lateral (E), todas na mesma altura de tela; embaixo, cada uma em tamanho real.
Inclui a Duende.png como referência de nível (só local, não sai da máquina).

Uso: python scripts/detail_before_after.py <saida.png>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

out = Path(sys.argv[1])
CHARS = Path("projects/default/characters")
ROWS = [
    ("antes: protótipo suave (128)", "aprendiz"),
    ("só acabamento: protótipo em pixel (192)", "aprendiz_pixel_192"),
    ("só modelagem: detalhado suave (128)", "aprendiz_detalhado_suave"),
    ("depois: detalhado em pixel (192)", "aprendiz_detalhado_192"),
]
VIEWS = ("S", "SE", "E")
CELL = 384
BG = (118, 150, 104)
INK = (20, 30, 20)
duende = Path.home() / "Documents/Pindorama/[Old] Pindorama Game/design/fontes-brutas/arte/8-frame/Duende.png"
sheet = Image.new("RGB", (260 + CELL * 3 + 3 * 200 + 420, CELL * len(ROWS)), BG)
draw = ImageDraw.Draw(sheet)
for r, (label, slug) in enumerate(ROWS):
    render = max((CHARS / slug / "stages/render").iterdir(), key=lambda p: p.stat().st_mtime)
    draw.text((8, r * CELL + CELL // 2), label, fill=INK)
    for c, d in enumerate(VIEWS):
        im = Image.open(render / f"frames/idle/{d}/idle_{d}_0000.png").convert("RGBA")
        big = im.resize((CELL, CELL), Image.NEAREST)
        sheet.paste(big, (260 + c * CELL, r * CELL), big)
        sheet.paste(im, (260 + CELL * 3 + c * 200 + (200 - im.width) // 2, r * CELL + CELL - im.height - 10), im)
if duende.exists():
    ref = Image.open(duende).convert("RGB").crop((60, 90, 340, 480))
    ref = ref.resize((int(ref.width * 1.4), int(ref.height * 1.4)), Image.NEAREST)
    x0 = sheet.width - 410
    sheet.paste(ref, (x0, 40))
    draw.text((x0, 10), "Duende.png (nível de referência)", fill=INK)
draw.text((260 + CELL * 3, 4), "tamanho real", fill=INK)
sheet.save(out)
print(out, sheet.size)
