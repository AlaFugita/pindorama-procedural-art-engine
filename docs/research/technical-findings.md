# Descobertas técnicas

Cada descoberta segue o mesmo roteiro: o problema que resolve, como funciona, onde está no código, vantagens, limites, aplicação no PPAE e complexidade.

## F1. Fábrica de asset com seed fixa e duas fases (rascunho → final)

- **Problema:** gerar variações reproduzíveis e escaláveis sem refazer o trabalho caro para cada candidato.
- **Como funciona:** `AssetFactory(factory_seed)` fixa uma seed por fábrica (`FixedSeed`, `int_hash`). Primeiro cria placeholders baratos (`create_placeholder`) para posicionar e testar; depois `finalize_placeholders` gera a geometria final. `asset_parameters(distance, vis_distance)` muda o detalhe conforme a distância da câmera.
- **Código:** `princeton-vl/infinigen` › `src/infinigen/core/placement/factory.py`.
- **Vantagens:**
  - reprodutível;
  - separa o "onde e quanto" do "como";
  - detalhe só onde aparece.
- **Limites:** feito para cenas grandes; no personagem, a "distância" equivale à resolução do sprite.
- **PPAE:**
  - a ficha ganha `seed` explícita (§13.1);
  - o build ganha modo rascunho, com malhas leves para testar enquadramento e pose;
  - a densidade de detalhe passa a depender da resolução (128 com menos peças finas; 192 e 256 com todas).
- **Complexidade:** baixa (seed) a média (rascunho).

## F2. Materiais como grafo de nós escrito em Python

- **Problema:** materiais ricos sem pintar imagens e sem um editor manual.
- **Como funciona:** o `NodeWrangler` encapsula o grafo de nós do Blender (`new_node`, `connect_input`, `expose_input`, `build_float_curve`). Cada material é uma função Python que monta o grafo; o de maçã, por exemplo, usa coordenadas de textura → Musgrave → Mix → RGB.
- **Código:** `infinigen` › `src/infinigen/core/nodes/node_wrangler.py`; exemplo em `src/infinigen/assets/objects/fruits/surfaces/apple_surface.py`.
- **Vantagens:** usa toda a biblioteca de texturas do Blender (ruído, Voronoi, onda, tijolo), com parâmetros e seed.
- **Limites:** o grafo fica verboso; o nó Musgrave mudou nas versões novas do Blender.
- **PPAE:** o canal de padrão do passe de luz (`stage_pixel_passes._pattern`) já é um grafo mínimo. Trocar a máscara binária por um **mini NodeWrangler próprio** permite combinar ruído, costura e desgaste num valor contínuo, como pede o §10 (tecido, couro, madeira, metal).
- **Complexidade:** média.

## F3. Grafo de material que vira um único shader (GLSL e Godot)

- **Problema:** o mesmo material precisa servir na geração offline e no runtime do Godot.
- **Como funciona:** cada nó gera declarações GLSL e uniforms (`ShaderCode`, `ShaderUniform`); o grafo é concatenado e compilado como um shader só (`gen_base.gd`, `shader_compute.gd`).
- **Código:** `RodZill4/material-maker` › `addons/material_maker/engine/nodes/gen_base.gd`.
- **Vantagens:** roda na GPU, é nativo do Godot e serve para runtime (§14.2).
- **Limites:** o PPAE gera sprites pré-renderizados; shader em runtime é só para efeitos (brilho, dissolver, tingir).
- **PPAE:** gerar um `.gdshader` de **tingimento por máscara de material**. Isso permite variar a cor da roupa em runtime sem renderizar de novo, e usa o passe `id` que já existe.
- **Complexidade:** média.

## F4. Ramificação Weber-Penn com orçamento

- **Problema:** árvores, raízes, cipós e chifres orgânicos e variados.
- **Como funciona:** ramificação recursiva por nível. Cada galho (`Stem`) tem segmentos, conicidade (`TaperProfile`) e raio por modelo; a espécie é um arquivo de parâmetros. `estimate_tree` e `check_mesh_stats` barram árvores que estouram o orçamento antes de gerar a malha.
- **Código:** `splatterfacegames/midori` › `crates/midori-core/src/generation.rs`, `tree.rs`.
- **Vantagens:** rico, parametrizado, determinístico (seed por variante `seed + i`).
- **Limites:** muitos parâmetros; o estilo é realista por padrão.
- **PPAE:** a técnica é **transferível**. A mesma curva com raio ao longo do comprimento (`point_at`, `radius_at`) serve para mechas de cabelo, cipós, chifres e caudas. O orçamento por estimativa serve para todo gerador.
- **Complexidade:** média (curva com conicidade) a alta (espécies completas).

## F5. Impostor assado por rasterizador de software

- **Problema:** mostrar geometria cara barata, com vistas fixas.
- **Como funciona:** um rasterizador com z-buffer desenha a copa de dois ângulos num atlas, e o LOD distante usa dois quads cruzados com esse atlas.
- **Código:** `midori` › `crates/midori-core/src/impostor.rs` (`bake_impostor`, `bake_view`).
- **Relação com o PPAE:** é exatamente o que o PPAE faz com sprites, só que no Blender. Confirma o desenho: render offline de vistas fixas → atlas → runtime barato.
- **Aplicação:** nenhuma mudança, só validação do caminho.

## F6. Contorno de forma por SDF

- **Problema:** formas orgânicas (folhas, pétalas, penas) sem modelar vértice a vértice.
- **Como funciona:** a forma é uma função de distância com sinal; `find_sdf_edge` acha a borda por bisseção ao longo de cada direção, e `generate_leaf_outline` gera o polígono com a resolução pedida.
- **Código:** `midori` › `crates/midori-core/src/leaves.rs`.
- **PPAE:**
  - SDF 2D para recortar abas e bordas de capa e capuz (barra rasgada, ponta de folha);
  - SDF 3D com remesh por voxel para unir peças orgânicas sem emendas. O voxel remesh já existe no build.
- **Complexidade:** média.

## F7. Luz única congelada para todos os assets

- **Problema:** assets gerados separadamente que não combinam entre si.
- **Como funciona:** a constante `SCENE_LIGHT` é usada por todo tile e prop; `toneRamp(base)` dá luz e sombra por mistura.
- **Código:** `dungeoncrab0606/procedural-tilemap-lab` › `tileShading.js`.
- **PPAE:** já é assim (luzes no `ArtProfile`). Falta garantir que **todo gerador futuro** leia a luz do perfil, como pede o §3.2.

## F8. Paleta em três níveis com aquecimento e esfriamento

- **Problema:** sombras sem vida (cinzas) e paletas desarmônicas.
- **Como funciona:** `shading_tiers` cria luz, base e sombra; `warm_shift`, `mute_color` e `recolor` mudam matiz e saturação.
- **Código:** `MozeeB/pixel-asset-gen` › `engine/palette.py`.
- **PPAE:** já implementado de forma mais completa (`ramp` em `pixel.py`, giro de matiz por material). **Confirmação**, sem ação.

## F9. Montagem modular com regras de vizinhança (WFC)

- **Problema:** construções e ambientes coerentes, sem peças incompatíveis lado a lado.
- **Como funciona:**
  1. Cada módulo declara conectores e probabilidade.
  2. O algoritmo escolhe a célula com menor entropia, propaga restrições e volta atrás se travar.
- **Código:** `marian42/wavefunctioncollapse` (README; o código é C# no Unity); `dropecho/dungen` oferece WFC e BSP em Haxe.
- **PPAE:** para o Building e o Environment Generator. Hoje **não aplicável**.
- **Complexidade:** alta.

## F10. Asset como função, com troca de pack de estilo

- **Problema:** mudar o estilo de tudo sem refazer cada asset.
- **Como funciona:** a cena referencia funções; o "pack" muda a implementação visual.
- **Fonte:** `elberacasa/seedbank`, só README (sem licença).
- **PPAE:** já existe a mesma ideia: ficha + gerador e `ArtProfile` com ramos toon, pixel e smooth. Para trocar o estilo de todo o catálogo basta trocar o perfil. **Confirmação.**

## F11. Auditoria de catálogo gerado

- **Problema:** gerar em escala acumula duplicatas, órfãos e versões velhas.
- **Como funciona:** varredura do manifesto contra os arquivos, com plano de limpeza revisável.
- **Código:** `procedural-tilemap-lab` › `generatedAssetAudit.js`.
- **PPAE:** entra no catálogo do §13.4, junto com o cache por hash.
- **Complexidade:** baixa.

## Respostas às perguntas da pesquisa

1. **Como outros softwares geram imagens complexas por código?**
   - Combinam muitos geradores simples e determinísticos: ramificação, ruído e módulos.
   - Usam grafos de material.
   - Fixam a seed e definem um orçamento.
   - Compõem tudo sob uma luz e uma paleta comuns.
2. **Melhores algoritmos por categoria:**
   - personagens: fonte 3D + render (o PPAE);
   - vegetação: Weber-Penn ou colonização;
   - terreno: mistura de ruídos com erosão;
   - estruturas: WFC ou BSP;
   - materiais: grafo de nós e rampa por material.
3. **Qualidade visual do PPAE:** padrão contínuo por grafo (F2), curvas com conicidade para mechas e cordões (F4), recorte por SDF (F6) e detalhe pela resolução (F1).
4. **Personagens mais orgânicos:** mechas por curva com conicidade e torção; capas com SDF e dobras; uniões por voxel e SDF; mais camadas de material (F2).
5. **Ambientes ricos:** Weber-Penn + espalhamento + WFC, quando chegar a vez (§17).
6. **Materiais, iluminação e animação:** grafo de material (F2/F3), luz do perfil para todos (F7), vento por pivô assado (midori, Pivot Painter) para natureza.
7. **Sem IA:** todos os projetos estudados geram sem IA. A qualidade vem de camadas de algoritmo, não de modelo generativo.
