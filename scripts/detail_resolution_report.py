"""Experimento de resolução: o mesmo Aprendiz detalhado em 128, 192 e 256 px por quadro.

Mede, por resolução: altura do personagem em pixels, pixels do rosto, cores distintas, memória
de vídeo (quadro cheio e recortado ao conteúdo), tamanho em disco dos atlases, tempo de render.
Gera a folha "tamanho real" (sem ampliação) e a folha ampliada à mesma altura de tela.

Uso: python scripts/detail_resolution_report.py <saida>
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
CHARS = Path("projects/default/characters")
SIZES = (128, 192, 256)
BG = (118, 150, 104)
report = {}
real = Image.new("RGB", (sum(SIZES) + 40 * 4, 300), BG)
same = Image.new("RGB", (3 * 520 + 40, 560), BG)
draw_real, draw_same = ImageDraw.Draw(real), ImageDraw.Draw(same)
x = 20
for i, size in enumerate(SIZES):
    slug = f"aprendiz_detalhado_{size}"
    render = max((CHARS / slug / "stages/render").iterdir(), key=lambda p: p.stat().st_mtime)
    frames = sorted((render / "frames").rglob("*.png"))
    heights, colors, bbox_px = [], set(), 0
    for path in frames:
        a = np.asarray(Image.open(path).convert("RGBA"))
        ys, xs = np.nonzero(a[..., 3])
        heights.append(ys.max() - ys.min() + 1)
        bbox_px += (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
        if path.parent.name == "S" and path.parent.parent.name == "idle":
            colors |= {tuple(c) for c in a[a[..., 3] > 0][:, :3].tolist()}
    atlases = sorted((Path("exports") / slug / "atlases").glob("*.png"))
    log = (Path("artifacts/chibi") / f"run_{slug}.log").read_text(encoding="utf-8", errors="replace")
    times = re.search(r"tempos: (\{.*\})", log)
    report[size] = {
        "frames": len(frames),
        "character_height_px": int(np.median(heights)),
        "colors_idle_S": len(colors),
        "vram_full_frames_mib": round(len(frames) * size * size * 4 / 2**20, 2),
        "vram_trimmed_mib": round(bbox_px * 4 / 2**20, 2),
        "atlas_disk_kib": round(sum(p.stat().st_size for p in atlases) / 1024, 1),
        "atlas_vram_mib": round(sum(np.prod(Image.open(p).size) * 4 for p in atlases) / 2**20, 2),
        "render_s": json.loads(times.group(1).replace("'", '"'))["render"] if times else None,
    }
    sample = Image.open(render / "frames/idle/SE/idle_SE_0000.png").convert("RGBA")
    real.paste(sample, (x, 300 - size - 10), sample)
    draw_real.text((x, 6), f"{size}px", fill=(20, 30, 20))
    x += size + 40
    k = 512 / size  # mesma altura de tela: o 128 é ampliado 4×, o 256 2×
    big = sample.resize((512, 512), Image.NEAREST)
    same.paste(big, (20 + i * 520, 40), big)
    draw_same.text((20 + i * 520, 10), f"{size}px ampliado {k:.2f}×", fill=(20, 30, 20))
real.save(out / "resolucoes_tamanho_real.png")
same.save(out / "resolucoes_mesma_altura.png")
(out / "resolucoes.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
for size, r in report.items():
    print(size, r)
