"""Teste de transparência nos PNG originais (quadros renderizados e atlases exportados).

Para cada arquivo verifica:
- modo RGBA com canal alpha real;
- borda do arquivo 100% transparente (sem fundo embutido) e nenhum pixel opaco cor de fundo;
- semitransparência só no contorno da silhueta (alpha parcial interno = fundo vazado);
- halo: pixel de borda semitransparente bem mais claro que os opacos vizinhos;
- cor escondida em alpha 0 (vaza com filtro bilinear no Godot).
Gera também uma prova visual do mesmo quadro sobre preto, branco e magenta, ampliado.

Uso: python scripts/master_audit_alpha.py <slug> <saida>
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

slug, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
render = max((Path("projects/default/characters") / slug / "stages/render").iterdir(), key=lambda p: p.stat().st_mtime)
files = sorted((render / "frames").rglob("*.png")) + sorted((Path("exports") / slug / "atlases").glob("*.png"))


def lum(rgb):
    return rgb[..., 0] * .299 + rgb[..., 1] * .587 + rgb[..., 2] * .114


def check(path):
    im = Image.open(path)
    result = {"mode": im.mode}
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    result["rgba"] = im.mode == "RGBA"
    border = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])
    result["border_opaque_px"] = int((border > 0).sum())
    opaque = alpha == 255
    partial = (alpha > 0) & (alpha < 255)
    magenta = (rgb[..., 0] > 200) & (rgb[..., 1] < 60) & (rgb[..., 2] > 200)
    result["opaque_magenta_px"] = int((magenta & (alpha > 0)).sum())
    # Semitransparente interno: cercado por opacos nos 4 vizinhos.
    pad = np.pad(opaque, 1)
    surrounded = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    result["interior_partial_px"] = int((partial & surrounded).sum())
    # Halo: borda semitransparente mais clara que TODOS os opacos num raio de 2 px, isto é,
    # uma cor que não pertence ao objeto (franja de fundo claro). Borda clara de peça clara não conta.
    ys, xs = np.nonzero(partial)
    halos = 0
    for y, x in zip(ys, xs):
        y0, y1, x0, x1 = max(0, y - 2), y + 3, max(0, x - 2), x + 3
        ring = opaque[y0:y1, x0:x1]
        if ring.any():
            ref = lum(rgb[y0:y1, x0:x1][ring]).max()
            if lum(rgb[y, x]) - ref > 30:
                halos += 1
    result["partial_px"] = int(partial.sum())
    result["halo_px"] = halos
    hidden = (alpha == 0) & (rgb.max(axis=-1) > 2)  # resíduo de 1/255 não vaza de forma visível
    result["hidden_rgb_px"] = int(hidden.sum())
    result["ok"] = (result["rgba"] and result["border_opaque_px"] == 0 and result["opaque_magenta_px"] == 0
                    and result["interior_partial_px"] == 0 and halos == 0)
    return result


report = {"render_folder": str(render), "files": len(files), "failures": {}, "totals": {}}
totals = {k: 0 for k in ("border_opaque_px", "opaque_magenta_px", "interior_partial_px", "halo_px", "partial_px", "hidden_rgb_px")}
for path in files:
    r = check(path)
    for k in totals:
        totals[k] += r[k]
    if not r["ok"]:
        report["failures"][str(path)] = r
report["totals"] = totals
report["modes"] = sorted({Image.open(p).mode for p in files})
report["passed"] = len(files) - len(report["failures"])
(out / "transparencia.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")

sample = Image.open(render / "frames/walk/SE/walk_SE_0002.png").convert("RGBA")
z = 4
proof = Image.new("RGBA", (128 * z * 3, 128 * z), (0, 0, 0, 255))
for i, bg in enumerate([(0, 0, 0, 255), (255, 255, 255, 255), (255, 0, 255, 255)]):
    tile = Image.new("RGBA", (128, 128), bg)
    tile.alpha_composite(sample)
    proof.paste(tile.resize((128 * z, 128 * z), Image.NEAREST), (i * 128 * z, 0))
proof.convert("RGB").save(out / "transparencia_fundos.png")
print(json.dumps({k: v for k, v in report.items() if k != "failures"}, ensure_ascii=False), "falhas:", len(report["failures"]))
