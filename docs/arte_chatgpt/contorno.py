"""Devolve o contorno escuro que some na redução para 128 px: 1 px marrom-escuro (40,28,24) por trás da figura,
calculado pela dilatação do alfa. Não mexe nos pixels da figura. Uso: python contorno.py arquivo.png [...]"""
import sys
import numpy as np
from PIL import Image, ImageFilter
COR = (40, 28, 24)
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGBA")
    a = im.getchannel("A")
    dil = a.filter(ImageFilter.MaxFilter(3))
    fundo = Image.new("RGBA", im.size, COR + (0,))
    fundo.putalpha(dil)
    fundo.alpha_composite(im)
    fundo.save(p)
    print("contorno", p)
