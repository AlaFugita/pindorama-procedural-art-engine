"""Folha de avaliação: 8 direções, caminhada e os sprites no tamanho real do jogo.

Uso: python scripts/chibi_sheet.py <saida.png> [slug ...]
"""

import sys
from pathlib import Path

from PIL import Image

EXPORTS = Path("projects/default/characters")
DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
BG = (96, 140, 84, 255)
out = Path(sys.argv[1])
slugs = sys.argv[2:] or ["aprendiz"]


def frame(slug, name):
    found = sorted(EXPORTS.glob(f"{slug}/stages/render/*/frames/**/{name}"), key=lambda p: p.stat().st_mtime)
    return found[-1] if found else None


rows = []
for slug in slugs:
    idle = [frame(slug, f"idle_{d}_0000.png") for d in DIRS]
    walk = [frame(slug, f"walk_SE_{i:04d}.png") for i in range(8)]
    rows += [idle, walk]
rows = [r for r in rows if all(r)]
if not rows:
    print(sorted(p.name for p in EXPORTS.glob(f"{slugs[0]}/**/*.png"))[:6])
    raise SystemExit("frames não encontrados")
zoom = 2
cell = 128 * zoom
sheet = Image.new("RGBA", (cell * 8, cell * len(rows) + 140), BG)
for y, row in enumerate(rows):
    for x, path in enumerate(row):
        im = Image.open(path).convert("RGBA").resize((cell, cell), Image.NEAREST)
        sheet.alpha_composite(im, (x * cell, y * cell))
# Tamanho real, sem ampliação, como no jogo.
y = cell * len(rows) + 6
for x, path in enumerate(rows[0]):
    sheet.alpha_composite(Image.open(path).convert("RGBA"), (x * 130 + 8, y))
sheet.convert("RGB").save(out)
print(out, sheet.size)
