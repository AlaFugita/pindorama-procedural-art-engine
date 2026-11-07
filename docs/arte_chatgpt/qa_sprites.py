"""QA de folhas de sprite vindas do ChatGPT (tiras de 8 quadros 128x128, RGBA).

Mede o que o olho perde quadro a quadro:
- altura da figura e linha do pé (escala e chão);
- deslocamento horizontal da cabeça entre quadros (tremida);
- cor média de pele, túnica verde e cabelo, comparada ao mestre (deriva de cor).

Uso: python qa_sprites.py prep/protagonista  -> lê <prefixo>_andar_<DIR>.png e <prefixo>_parado_<DIR>.png
Saída: tabela no terminal e <prefixo>_qa.json. Não altera nenhuma imagem.
"""
import sys, json, colorsys
import numpy as np
from PIL import Image

DIRS = ["E", "SE", "S", "NE", "N"]
CEL = 128


def quadros(path):
    im = np.asarray(Image.open(path).convert("RGBA")).astype(float)
    return [im[:, i * CEL:(i + 1) * CEL] for i in range(im.shape[1] // CEL)]


def mascaras(q):
    rgb, a = q[..., :3] / 255.0, q[..., 3] > 128
    mx, mn = rgb.max(-1), rgb.min(-1)
    v, s = mx, np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(v)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, h)
    h = np.where(mx == g, (b - r) / d + 2, h)
    h = np.where(mx == b, (r - g) / d + 4, h)
    h = h * 60
    pele = a & (h >= 12) & (h <= 35) & (s > 0.40) & (s < 0.80) & (v > 0.55)
    verde = a & (h >= 70) & (h <= 150) & (s > 0.25) & (v > 0.20)
    cabelo = a & (v < 0.22) & (s < 0.6)
    return a, {"pele": pele, "verde": verde, "cabelo": cabelo}


def mede(q):
    a, ms = mascaras(q)
    ys, xs = np.nonzero(a)
    if len(ys) == 0:
        return None
    topo, pe = ys.min(), ys.max()
    alt = pe - topo + 1
    cab = a.copy(); cab[int(topo + alt * 0.30):] = False  # terço de cima = cabeça
    cx = float(np.nonzero(cab)[1].mean())
    cores = {}
    for k, m in ms.items():
        cores[k] = (q[..., :3][m].mean(0).round(1).tolist() if m.sum() > 20 else None)
    return {"alt": int(alt), "pe": int(pe), "cabeca_x": round(cx, 1), "cores": cores,
            "px_pele": int(ms["pele"].sum())}


def dist(c1, c2):
    return None if c1 is None or c2 is None else round(float(np.linalg.norm(np.array(c1) - np.array(c2))), 1)


def main(prefixo):
    mestre = {d: mede(quadros(f"{prefixo}_parado_{d}.png")[0]) for d in DIRS}
    ref = {k: np.mean([m["cores"][k] for m in mestre.values() if m["cores"][k]], 0).tolist() for k in ["pele", "verde", "cabelo"]}
    rel = {"ref_cores": ref, "dirs": {}}
    print(f"{'dir':4} {'alt min-max':12} {'pe':8} {'tremida cabeça':15} {'Δpele':>6} {'Δverde':>7} {'Δcabelo':>8}")
    for d in DIRS:
        ms = [mede(q) for q in quadros(f"{prefixo}_andar_{d}.png")]
        alts = [m["alt"] for m in ms]; pes = [m["pe"] for m in ms]; cxs = [m["cabeca_x"] for m in ms]
        salto = max(abs(cxs[i] - cxs[i - 1]) for i in range(len(cxs)))
        dp = [dist(m["cores"]["pele"], ref["pele"]) for m in ms]
        dv = [dist(m["cores"]["verde"], ref["verde"]) for m in ms]
        dc = [dist(m["cores"]["cabelo"], ref["cabelo"]) for m in ms]
        mx = lambda l: max([x for x in l if x is not None], default=None)
        rel["dirs"][d] = {"quadros": ms, "alt": [min(alts), max(alts)], "pe": sorted(set(pes)),
                          "cabeca_x": cxs, "maior_salto_cabeca_px": round(salto, 1),
                          "dpele_max": mx(dp), "dverde_max": mx(dv), "dcabelo_max": mx(dc)}
        print(f"{d:4} {min(alts):3}-{max(alts):<8} {str(sorted(set(pes))):8} amp {max(cxs)-min(cxs):4.1f} salto {salto:4.1f} {mx(dp)!s:>6} {mx(dv)!s:>7} {mx(dc)!s:>8}")
    json.dump(rel, open(f"{prefixo}_qa.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
