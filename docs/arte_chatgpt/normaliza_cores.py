"""Corrige a deriva de cor entre folhas do ChatGPT: leva a média de cada material (pele, túnica verde, cabelo)
de cada tira para a média do mestre parado, com um ganho por canal (limitado a 0,85-1,20) aplicado só na máscara do material.
A mesma correção vale para os 8 quadros da tira, para não criar tremida de cor dentro da animação.

Uso: python normaliza_cores.py prep/protagonista  -> grava <prefixo>_andar_<DIR>.png corrigido e guarda o original em <prefixo>_andar_<DIR>_bruto.png
"""
import sys, os, shutil
import numpy as np
from PIL import Image, ImageFilter
from qa_sprites import DIRS, CEL, quadros, mascaras, mede


def main(prefixo):
    mestre = [mede(quadros(f"{prefixo}_parado_{d}.png")[0]) for d in DIRS]
    ref = {k: np.mean([m["cores"][k] for m in mestre if m["cores"][k]], 0) for k in ["pele", "verde", "cabelo"]}
    for d in DIRS:
        path = f"{prefixo}_andar_{d}.png"
        bruto = f"{prefixo}_andar_{d}_bruto.png"
        if not os.path.exists(bruto):
            shutil.copy(path, bruto)
        im = np.asarray(Image.open(bruto).convert("RGBA")).astype(float)
        _, ms = mascaras(im)
        out = im.copy()
        for k, m in ms.items():
            if m.sum() < 50:
                continue
            ganho = np.clip(ref[k] / np.maximum(im[..., :3][m].mean(0), 1), 0.85, 1.20)
            # máscara suave: 1 no material, rampa de 1 px nas bordas para não desenhar contorno de correção
            suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
            fator = 1 + (ganho - 1) * suave[..., None]
            out[..., :3] = out[..., :3] * fator
            print(d, k, "ganho", ganho.round(3).tolist())
        Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)


if __name__ == "__main__":
    main(sys.argv[1])
