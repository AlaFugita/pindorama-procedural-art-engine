# Sistema de detalhamento artístico

**Data:** 2026-11-07. **Referência de nível:** `Duende.png` (Pindorama, `design/fontes-brutas/arte/8-frame/`).
**Personagem de validação:** Aprendiz. Rig, animação, contratos e pipeline foram mantidos.
**Aprovação artística:** humana; G9 não foi aprovado.

## 1. Diagnóstico do sistema anterior

| Pergunta | Resposta encontrada no código | Onde |
|---|---|---|
| Peças com primitivas simples | **Todas** as peças chibi: elipsoides, cápsulas, tubos, lofts verticais e caixas. Algumas passam por remesh por voxel e suavização | `chibi_components.py`, `geometry.py` |
| Peças com geometria detalhada | Nenhuma no Aprendiz. Só a malha da Rota C t09 (TripoSG + base CC0), que não é usada nele | `library/masters/guardiao_t09/` |
| UV maps | **Não existem** nas peças chibi: as malhas nascem por `from_pydata`, sem UV. Só a base CC0 da Rota A tinha UV | `stage_build._make_mesh` |
| Texturas pintadas | **Nenhuma** no Aprendiz. A pintura por cor de vértice existia só nos testes da Rota C (`paint/t03–t05`) | `body_paint.py` |
| Normal maps | **Nenhum** em todo o projeto | — |
| Materiais | Um por cor: Diffuse branco → Shader to RGB → rampa constante de 3 degraus × cor base → Emissão. Sem rugosidade, metal ou especular | `materials.toon_material` |
| Sombras | Só por N·L na rampa. A sombra projetada foi **desligada** no perfil chibi (`light_shadows: false`), porque a casca de contorno sombreava o corpo. Sem oclusão | `scene.add_lights` |
| Contorno | Casca invertida (Solidify 0,017 m, normais viradas, backface culling), cor = base × 0,055. Espessura uniforme; sem linhas internas, a não ser onde peças se sobrepõem | `stage_build._add_outline` |
| Pixel art | **Não existia.** O render era suave, com antialiasing (filtro 1,1 px, 32 amostras) e alpha semitransparente | `isometric_chibi_v1` |

**Conclusão:** a falta de riqueza não vinha da resolução. Vinha de quatro coisas:

1. A forma tinha poucas camadas: nada de dobras, costuras, sola, fivela ou pálpebra.
2. Todo material era igual: mesma rampa e nenhuma diferença entre couro, tecido, metal e madeira.
3. Não havia sombra projetada nem oclusão.
4. Não havia acabamento de pixel: o contorno uniforme e o antialiasing apagam a leitura por clusters.

Aumentar a resolução do render antigo só mostraria as mesmas primitivas lisas em mais pixels.

## 2. Arquitetura atualizada

O que muda fica em **duas camadas**. Rig, animação, contratos de ficha, gates e exportação continuam iguais.

```
CharacterSpec → resolver → build (peças) → rig → animate ─┬→ render suave (perfil sem "pixel")
                                                          └→ pixel_passes (Blender) → compose (Python) → frames
                                                                       mesmo formato de frames → post, atlases, gates, Godot
```

**Camada 1: modelagem em camadas** (`blender/scripts/ics_blender/chibi_detail.py`, assets `chibi_*_detail_v1`)

| Pedido | Implementado no Aprendiz | Técnica |
|---|---|---|
| Rosto expressivo | Branco do olho, íris, pupila, dois brilhos, pálpebra grossa no canto, sobrancelha, nariz, boca em sorriso, bochecha | Peças finas sobre a superfície da cabeça, cada uma com papel de material |
| Cabelo | Cabeleira + 6 mechas de franja afiladas + 2 mechas laterais | `strip` com largura que afina até a ponta |
| Roupas em camadas | Capuz, capinha, túnica, cinto, alça, braçadeira | Peças separadas: a linha interna nasce da sobreposição |
| Capuz e capa com dobras | Dobras radiais que crescem para a barra; frente mais lisa | `fold_loft`; deslocamento no capuz |
| Botas, luvas e acessórios | Sola, biqueira, cano dobrado, cadarço, braçadeira com tiras, bolsinha, bolsa com fecho e berloque | Primitivas pequenas com papel próprio |
| Arma com detalhes | Empunhadura enrolada, anéis de metal, espiral, orbe luminoso | Tubos e anéis; orbe com papel emissivo |
| Ornamentos | Broche no peito, fivela, costura central do capuz | Metal e linha de costura |

**Camada 2: acabamento pixel art nativo** (`stage_pixel_passes.py` + `engines/postprocess_engine/pixel.py`)

1. O Blender renderiza **na grade final** (128, 192 ou 256), com 1 amostra para identidade e profundidade, filtro 0 e transformação Raw. Não há redução de uma imagem maior.
2. Passes por quadro:
   - `id`: índice da peça;
   - `light`: luz direcional **com sombra projetada** (a casca 3D sai, então a sombra volta), oclusão ambiente e máscara de padrão;
   - `depth`: profundidade em 16 bits.
3. A composição decide cada pixel por regra:
   - papel do material pela peça;
   - tom na rampa, como luz × oclusão;
   - matiz girando nas sombras;
   - brilho só em cabelo, metal e gema;
   - padrão (costura, couro, veio da madeira) como um degrau de tom.
4. Linhas internas aparecem onde a profundidade salta: entre peças com o limite do perfil, dentro da mesma peça só com salto 2,6× maior. O contorno externo fica 1 px **fora** da silhueta, em contorno seletivo: tinta escura misturada ao tom mais escuro do material, mais leve no lado iluminado.
5. Ilhas de 1 px são absorvidas pelo tom vizinho, exceto em materiais protegidos (olhos, boca, gema). Materiais emissivos ganham anel de brilho. O alpha é binário.

**Texturização:**

- Dobras, costuras, couro e veio da madeira viram geometria e padrão em coordenadas do objeto, que acompanham o giro.
- Variação de tom vem da rampa de matiz.
- Metal tem brilho próprio; pintura e ornamentos são peças.

Não há UV nem textura em imagem. Na escala do jogo, um texel pintado vira menos de 1 pixel, e a regra por material dá controle melhor. UV e normal map ficam para quando houver modelagem esculpida (seção 8).

## 3. Perfil artístico `pindorama_pixel_art_detailed_v1`

Arquivo: [`library/profiles/art/pindorama_pixel_art_detailed_v1.json`](../library/profiles/art/pindorama_pixel_art_detailed_v1.json). Gerador: `scripts/gen_pixel_profile.py`. Contrato: `PixelArtSettings` e `PixelMaterialRole` em `contracts.py`.

| Pedido | No perfil |
|---|---|
| Paleta de cores | A cor base vem da peça (paleta da ficha), então a variação de cor continua funcionando. Metal e gema têm base fixa. Por material: faixa de brilho e giro de matiz |
| Densidade de detalhes | Definida pelas peças `*_detail_v1` e pelo `cluster_min_px` = 2 |
| Espessura de contorno | 1 px fora da silhueta; linhas internas de 1 px |
| Tons por material | Pele 4; cabelo 4 + brilho; tecido 4; borda clara 3; couro 4; couro escuro 3; madeira 3; metal 3 + brilho; gema 3 emissiva; olhos e tinta 1 |
| Sombras | Luz principal a 50° com sombra projetada; limiares 0,20 / 0,42 / 0,66; oclusão de 30 a 65% por material |
| Highlights | Só cabelo, metal e gema, acima de um limiar próprio |
| Clusters | Mínimo 2 px; olhos, boca e gema protegidos |
| Resolução de referência | 192 px (veja a seção 5) |
| Transparência | Binária: 0 ou 255; RGB zerado onde alpha = 0; nenhum halo |

## 4. Antes e depois

[audit/detalhamento/antes_depois.png](audit/detalhamento/antes_depois.png) é uma matriz 2×2: geometria (protótipo × detalhada) cruzada com acabamento (suave × pixel). Mostra as vistas frontal, três quartos e lateral, em tamanho real ao lado, com a Duende.png como referência de nível.

O acabamento sozinho já muda a leitura: tons, contorno e textura de pixel. A modelagem sozinha traz rosto, metal e acessórios. As duas juntas formam o "depois".

Caminhada no novo padrão: [walk_8dir.gif](audit/detalhamento/animacoes/walk_8dir.gif) e [walk_quadros.png](audit/detalhamento/animacoes/walk_quadros.png).

## 5. Teste nas três resoluções

Os números estão em [resolucoes.json](audit/detalhamento/resolucao/resolucoes.json). As folhas são [tamanho real](audit/detalhamento/resolucao/resolucoes_tamanho_real.png) e [mesma altura de tela](audit/detalhamento/resolucao/resolucoes_mesma_altura.png); os GIFs ficam em `animacoes_128/` e `animacoes_256/`.

| Quadro | Altura do personagem | VRAM, 192 quadros cheios | VRAM recortada | Atlas em disco | Render (3 clips × 8 direções) |
|---|---|---|---|---|---|
| 128 | 97 px | 12,0 MiB | 4,2 MiB | 420 KiB | 69 s |
| 192 | 145 px | 27,0 MiB | 9,2 MiB | 684 KiB | 83 s |
| 256 | 192 px | 48,0 MiB | 16,3 MiB | 984 KiB | 100 s |

- **Legibilidade:**
  - **128:** o rosto ainda lê, mas a borda felpuda e os metais viram 1 px.
  - **192:** olhos com brilho, borda, fivela e orbe ficam claros.
  - **256:** pouco ganho visível sobre 192.
- **Riqueza:** a quantidade de cores quase não muda (76 a 79). A riqueza vem do modelo e do perfil, não da resolução.
- **Movimento:**
  - Em 128, os detalhes de 1 px piscam mais entre quadros.
  - Em 192 também há uma piscada: a costura de 1 px nas costas do capuz falha em alguns quadros da caminhada.
- **MMORPG:**
  - **Memória:** VRAM sem compressão é `largura × altura × 4` por quadro. Só com idle, walk e run, o 192 custa 27 MiB por personagem sem recorte e 9 MiB com recorte. Com os clips que faltam (ataque, magia, dano, morte), isso tende a triplicar. Muitos personagens únicos na tela exigem atlas recortado, que hoje o atlas não faz, e carregamento sob demanda.
  - **Desempenho:** o custo de desenho é igual nas três resoluções (um quad por sprite). O limite é a memória.

**Proposta, não decisão:** **192** como referência, desde que o atlas passe a recortar o quadro. 128 como nível reduzido para multidões; 256 só para retratos ou cenas.

## 6. Evidências de renderização

| Evidência | Arquivo |
|---|---|
| Oito direções no novo padrão | [oito_direcoes_idle.png](audit/detalhamento/oito_direcoes_idle.png), [oito_direcoes_walk.png](audit/detalhamento/oito_direcoes_walk.png) |
| GIFs idle, walk e run (no lugar e no mundo) | [audit/detalhamento/animacoes/](audit/detalhamento/animacoes/) |
| Transparência: 216/216 aprovados | [transparencia.json](audit/detalhamento/transparencia/transparencia.json) |
| Sonda de chão e túnica no modelo detalhado | [sonda.json](audit/detalhamento/sonda.json): sola +0,5 mm; coxa igual ao mestre |
| Pipeline até o Godot, nas três resoluções | G1, G7 e G8 PASS; G6 WARN (idle repetido); G3, G4, G5 e G9 REVIEW |
| Testes unitários do compositor | `tests/unit/test_pixel_compose.py` (5 testes) |

## 7. Impacto no pipeline

- **Contrato:** `ArtProfile.pixel` é opcional. Perfis antigos continuam iguais e os 47 testes antigos passam; com os novos, são 52.
- **Pipeline:** um ramo na etapa de render (`_render_pixel`). O cache considera o perfil pixel e o código do compositor. Pós-produção, atlases, gates e Godot não mudaram.
- **Build:** grava `ics_color` e o `mesh_sha` de cada peça; o hash serve para a prova modular.
- **Custo:** o render pixel leva de 69 a 100 s contra 27 s do suave, por fazer três passes por quadro.
- **Limite:** até 254 peças por personagem, por causa do índice de 8 bits.
- **Godot:** importar sem compressão VRAM e com filtro Nearest, como pede a documentação para pixel art. O manifesto ainda não define isso.

## 8. Critérios de qualidade e limitações

**Para o usuário julgar, sem aprovação automática:**

1. A diferença em relação ao protótipo é perceptível em rosto, roupa, material e contorno?
2. Lê bem no tamanho real de 192?
3. Desenho liso ou pixel art?
4. A resolução de referência pode ser 192?

**Limitações, com honestidade:**

- **Distância da Duende:** ela tem mais contraste e saturação, contorno mais escuro, muito mais ornamentos (sinos e glifos bordados), tecido rasgado, partículas de brilho e pose expressiva. O Aprendiz ainda tem grandes áreas de azul chapado no capuz.
- **Escultura:** tudo continua procedural. Não há escultura nem normal map. Rosto e mãos seguem simples perto de um sprite pintado à mão.
- **Cores:** o perfil prevê 64 cores, mas medi 76 a 79 no idle S. O limite ainda não é aplicado.
- **Linhas finas:** linhas de 1 px, como a costura do capuz, piscam em movimento.
- **Expressão:** a animação é procedural e sem expressão facial, e o rosto não muda.
- **IA de textura:** não encontrei ferramenta local e aberta de IA para material que valha incorporar. O Material Maker (MIT, procedural) é o candidato, se um dia houver textura em imagem. Nada foi enviado para fora da máquina.

## Fontes

- [Blender: Shader to RGB](https://docs.blender.org/manual/en/4.0/render/shader_nodes/converter/shader_to_rgb.html)
- [Godot: importar imagens](https://docs.godotengine.org/en/4.5/tutorials/assets_pipeline/importing_images.html)
- [Lospec: contornos com cor](https://lospec.com/articles/pixel-art-outlines-part-2-using-color)
- [Pixnote: sombra e matiz](https://pixnote.net/en/learn/shading)
- [SLYNYRD: paletas](https://www.slynyrd.com/blog/2018/1/10/pixelblog-1-color-palettes)
- [Elliot Bentine: pixelizar objetos 3D](https://medium.com/@elliotbentine/pixelizing-3d-objects-b55ec33328f1)
- [Material Maker (listagem)](https://awesome.ecosyste.ms/projects/github.com%2FRodZill4%2Fmaterial-maker)
