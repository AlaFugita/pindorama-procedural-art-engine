# Batalha na Clareira (cena simulada)

Cena jogável para ver o jogo "em movimento": o protagonista indígena contra uma criatura da mata.
Página: `site/jogar.html` (GitHub Pages) e o artifact privado do usuário.

## Arte (ChatGPT, conferida e corrigida por código)
| Folha | Tentativas | QA |
|---|---|---|
| `bruto/fundo_floresta_t1.png` | 1 | clareira aberta no centro, sem personagens |
| `bruto/bicho_andar_E_t1.png`, `bicho_ataque_E_t1.png` | 1 cada | criatura original (casca, musgo, folhas); escala única pela postura neutra (`--ref 1`) |
| `bruto/heroi_golpe_E_t1.png` | 2 | na 1ª, o ChatGPT recusou "golpe de cajado"; "floreio com o cajado" passou |
| `bruto/heroi_disparo_E_t1.png`, `heroi_magia_E_t1.png` | 1 cada | a magia veio ~7% menor; a escala pelo quadro 1 iguala |
| `bruto/heroi_ferido_E_t1.png` | 1 | **quadro 7 com cajado duplicado** e troca de mão; o jogo usa só os quadros 1 a 5 |

## Preparo
- `prep_acao.py`: ações ancoradas pelo **tronco** (centro da túnica) e não pela caixa. Com isso o corpo não treme quando o cajado sai para os lados. Quadro de 192×128 e pé no pixel 124.
- Criatura: `preparar_liso.py andar --cw 192 --ch 160 --alt 112 --ref 1`.
- Contorno de 1 px: `../arte_chatgpt/contorno.py`.

## Código (`site/index.html`)
Movimento em 8 direções (o oeste é espelhado), IA do herói (modo demonstração) e da criatura (aviso vermelho no chão antes do bote).
Também em código: golpe, semente de luz, raízes da mata (área e atordoamento), esquiva, cura, números de dano, crítico, empurrão, tremor de tela e HUD.
Números de combate e câmera são provisórios, não são cânone.
