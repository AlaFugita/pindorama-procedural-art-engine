"""Junta as vistas chibi ao Mago de referência. Uso: python scripts/chibi_compare.py <pasta>"""

import sys
from pathlib import Path

from PIL import Image

REF = Path.home() / "Documents/Pindorama/[Old] Pindorama Game/design/docs/arte/referencias/mago_referencia_jogo.png"
folder = Path(sys.argv[1])
ours = Image.open(folder / "vistas.png").convert("RGB").crop((0, 0, 1536, 512))
ref = Image.open(REF).convert("RGB")
ref = ref.resize((int(ref.width * 512 / ref.height), 512), Image.NEAREST)
sheet = Image.new("RGB", (ours.width + ref.width, 512), (255, 0, 255))
sheet.paste(ours, (0, 0))
sheet.paste(ref, (ours.width, 0))
sheet.save(folder / "ab.png")
