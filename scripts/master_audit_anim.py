"""Auditoria das animações do personagem mestre a partir dos PNG originais.

Gera, por clip:
- ``<clip>_8dir.gif``: as oito direções no lugar, na velocidade do jogo (fps do manifesto);
- ``<clip>_8dir_mundo.gif``: o sprite andando no chão à ``ground_speed_mps``, com marcas fixas
  no chão. O pé de apoio deve ficar parado em relação às marcas (deslizamento visível);
- ``<clip>_quadros.png``: oito direções × todos os quadros, para inspeção quadro a quadro.

Uso: python scripts/master_audit_anim.py <slug> <saida>
"""

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

slug, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
root = Path("projects/default/characters") / slug / "stages/render"
render = max(root.iterdir(), key=lambda p: p.stat().st_mtime)
manifest = json.loads((Path("exports") / slug / "manifest.json").read_text(encoding="utf-8"))
profile = json.loads((Path("library/profiles/render") / f"{manifest['render_profile']}.json").read_text(encoding="utf-8"))
ppm = profile["pixels_per_meter"]
elev = math.radians(profile["elevation_deg"])
DIRS = manifest["direction_order"]
BG = (118, 150, 104)
LABEL = (20, 30, 20)
Z = 2
SIZE = profile["canvas"]["width"]
CELL = SIZE * Z


def frames(clip, d):
    folder = render / "frames" / clip / d
    return [Image.open(p).convert("RGBA") for p in sorted(folder.glob(f"{clip}_{d}_*.png"))]


def heading_vector(d):
    """Deslocamento em tela por metro andado (câmera ao sul, olhando ao norte)."""
    h = math.radians(profile["headings_deg"][d])
    wx, wy = math.sin(h), math.cos(h)
    return wx * ppm * Z, -wy * ppm * math.sin(elev) * Z


summary = {"render_folder": str(render), "clips": {}}
for anim in manifest["animations"]:
    clip, fps, n = anim["animation"], anim["fps"], anim["frame_count"]
    speed = anim["ground_speed_mps"]
    seq = {d: frames(clip, d) for d in DIRS}
    assert all(len(v) == n for v in seq.values()), (clip, {d: len(v) for d, v in seq.items()})
    ms = round(1000 / fps)

    # 1. No lugar, oito direções, grade 4×2.
    gif = []
    for i in range(n):
        sheet = Image.new("RGB", (CELL * 4, CELL * 2 + 18), BG)
        draw = ImageDraw.Draw(sheet)
        for k, d in enumerate(DIRS):
            x, y = (k % 4) * CELL, (k // 4) * CELL
            sheet.paste(seq[d][i].resize((CELL, CELL), Image.NEAREST), (x, y), seq[d][i].resize((CELL, CELL), Image.NEAREST))
            draw.text((x + 6, y + 4), d, fill=LABEL)
        draw.text((6, CELL * 2 + 3), f"{slug} {clip} {fps} fps quadro {i}/{n}", fill=LABEL)
        gif.append(sheet)
    gif[0].save(out / f"{clip}_8dir.gif", save_all=True, append_images=gif[1:], duration=ms, loop=0, disposal=2)

    # 2. No mundo: o personagem anda; marcas do chão ficam fixas.
    cycles = 3
    span = int(SIZE * 2.3) * Z // 2
    world = []
    for i in range(n * cycles):
        sheet = Image.new("RGB", (span * 4, span * 2 + 18), BG)
        draw = ImageDraw.Draw(sheet)
        t = i / fps
        for k, d in enumerate(DIRS):
            ox, oy = (k % 4) * span, (k // 4) * span
            vx, vy = heading_vector(d)
            dist = speed * t
            start_x = ox + span / 2 - vx * speed * n * cycles / fps / 2
            start_y = oy + span / 2 + 40 - vy * speed * n * cycles / fps / 2
            for m in range(-6, 7):  # marcas a cada 10 cm ao longo do trajeto
                mx = start_x + vx * m * .1 + vx * speed * n * cycles / fps / 2
                my = start_y + vy * m * .1 + vy * speed * n * cycles / fps / 2
                draw.ellipse((mx - 2, my - 1, mx + 2, my + 1), fill=(70, 100, 60))
            px, py = start_x + vx * dist, start_y + vy * dist
            sprite = seq[d][i % n].resize((CELL, CELL), Image.NEAREST)
            pivot = anim["directions"][d]["pivot"]
            sheet.paste(sprite, (int(round(px - pivot["x"] * Z)), int(round(py - pivot["y"] * Z))), sprite)
            draw.text((ox + 6, oy + 4), d, fill=LABEL)
        draw.text((6, span * 2 + 3), f"{slug} {clip} no mundo, {speed} m/s, {fps} fps", fill=LABEL)
        world.append(sheet)
    if speed > 0:
        world[0].save(out / f"{clip}_8dir_mundo.gif", save_all=True, append_images=world[1:], duration=ms, loop=0, disposal=2)

    # 3. Quadros lado a lado: linhas = direções, colunas = quadros (+ o primeiro repetido para checar o laço).
    z = 1.5
    c = int(SIZE * z)
    sheet = Image.new("RGB", (c * (n + 1) + 40, c * 8), BG)
    draw = ImageDraw.Draw(sheet)
    for r, d in enumerate(DIRS):
        draw.text((4, r * c + c // 2), d, fill=LABEL)
        for i in range(n + 1):
            im = seq[d][i % n].resize((c, c), Image.NEAREST)
            sheet.paste(im, (40 + i * c, r * c), im)
        # Linha do chão no pivô.
        gy = r * c + int(anim["directions"][d]["pivot"]["y"] * z)
        draw.line((40, gy, sheet.width, gy), fill=(80, 112, 70))
    sheet.save(out / f"{clip}_quadros.png")
    summary["clips"][clip] = {"fps": fps, "frames": n, "ground_speed_mps": speed, "frame_ms": ms}

(out / "resumo.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
