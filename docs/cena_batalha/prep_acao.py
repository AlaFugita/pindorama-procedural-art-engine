"""Prepara folhas de AÇÃO do ChatGPT (grade 4x2, fundo magenta) ancorando cada quadro pelo TRONCO, não pela caixa.

Por quê: numa ação o cajado ou o corpo saem para os lados; centralizar pela caixa faria o corpo tremer de quadro a quadro.
Aqui: a escala vem do quadro de referência (postura neutra) para casar com o andar; o x de ancoragem é o centro da túnica verde
(com mediana entre as linhas do tronco) e o y é o pé mais baixo.

Uso: python prep_acao.py FOLHA.png SAIDA.png --alt 108 --cw 192 --ch 128 [--ref 1] [--troca 7=6]
  --troca 7=6  substitui o quadro 7 pelo 6 (para quadro com erro de desenho)
Grava SAIDA (tira 8 x cw) e imprime o deslocamento do tronco medido.
"""
import sys, argparse, importlib.util
import numpy as np
from PIL import Image

spec = importlib.util.spec_from_file_location("pl", sys.argv[0].replace("prep_acao.py", "preparar_liso.py"))


def recorta_fundo(rgb):
    from PIL import ImageFilter
    a = rgb.astype(int)
    d = np.sqrt((a[..., 0] - 255) ** 2 + a[..., 1] ** 2 + (a[..., 2] - 255) ** 2)
    fundo = d < 110
    tinge = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]
    perto = np.array(Image.fromarray((fundo * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    m = ~(fundo | (perto & (tinge > 35)))
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))) > 0
    return np.dstack([rgb, (m * 255).astype(np.uint8)])


def tronco_x(rgba):
    rgb = rgba[..., :3].astype(int); a = rgba[..., 3] > 128
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    verde = a & (g > r + 8) & (g > b + 25)   # túnica
    ys, xs = np.nonzero(verde)
    if len(xs) < 50:
        ys, xs = np.nonzero(a)
    return float(np.median(xs))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("folha"); p.add_argument("saida")
    p.add_argument("--alt", type=int, default=108); p.add_argument("--cw", type=int, default=192); p.add_argument("--ch", type=int, default=128)
    p.add_argument("--ref", type=int, default=1); p.add_argument("--troca", nargs="*", default=[])
    p.add_argument("--ancora", choices=["tronco", "caixa"], default="tronco")
    o = p.parse_args()
    im = np.asarray(Image.open(o.folha).convert("RGB"))
    H, W = im.shape[:2]; cw0, ch0 = W // 4, H // 2
    quadros = []
    for j in range(2):
        for i in range(4):
            q = recorta_fundo(im[j * ch0:(j + 1) * ch0, i * cw0:(i + 1) * cw0])
            quadros.append(q)
    for t in o.troca:
        a_, b_ = map(int, t.split("=")); quadros[a_ - 1] = quadros[b_ - 1]
    ys = np.nonzero(quadros[o.ref - 1][..., 3] > 128)[0]
    esc = o.alt / (ys.max() - ys.min() + 1)
    pe_alvo = o.ch - 4
    tira = Image.new("RGBA", (o.cw * 8, o.ch), (0, 0, 0, 0))
    medidas = []
    for k, q in enumerate(quadros):
        img = Image.fromarray(q)
        # alfa pré-multiplicado na redução para não escurecer/rosar a borda
        arr = np.asarray(img).astype(float); al = arr[..., 3:4] / 255.0
        pre = Image.fromarray(np.dstack([arr[..., :3] * al, arr[..., 3]]).astype(np.uint8))
        nw, nh = max(1, round(q.shape[1] * esc)), max(1, round(q.shape[0] * esc))
        red = np.asarray(pre.resize((nw, nh), Image.LANCZOS)).astype(float)
        a2 = red[..., 3:4] / 255.0
        rgb = np.where(a2 > 0, red[..., :3] / np.maximum(a2, 1e-6), 0)
        red = np.dstack([np.clip(rgb, 0, 255), red[..., 3]]).astype(np.uint8)
        al = red[..., 3] > 128
        yy, xx = np.nonzero(al)
        ax = tronco_x(red) if o.ancora == "tronco" else (xx.min() + xx.max()) / 2
        pe = yy.max()
        ox, oy = round(o.cw / 2 - ax), round(pe_alvo - pe)
        cel = Image.new("RGBA", (o.cw, o.ch), (0, 0, 0, 0))
        cel.alpha_composite(Image.fromarray(red), (ox, oy)) if ox >= 0 and oy >= 0 else cel.paste(Image.fromarray(red), (ox, oy), Image.fromarray(red))
        c = np.asarray(cel)[..., 3] > 0
        borda = c[:, 0].any() or c[:, -1].any() or c[0, :].any()
        tira.alpha_composite(cel, (k * o.cw, 0))
        medidas.append((k + 1, round(ax - xx.min(), 1), int(yy.max() - yy.min() + 1), "BORDA" if borda else ""))
    tira.save(o.saida)
    print("escala", round(esc, 4), "quadros (n, tronco-x dentro da figura, altura, aviso):", medidas)


if __name__ == "__main__":
    main()
