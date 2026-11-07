# Catálogo técnico de repositórios de geração procedural

**Data:** 2026-11-07.

Os metadados vêm da API do GitHub: licença, linguagem, estrelas e último push.

Cada informação técnica traz a sua fonte:

- **[código]**: lido no arquivo citado;
- **[doc]**: tirado do README;
- **[hipótese]**: inferência minha.

**Profundidade:** estudo proporcional à relevância. Personagens, materiais e vegetação receberam leitura de código; mapas e terreno, só leitura de README.

| # | Projeto | Linguagem | Licença | Atividade | Categoria | Gera assets? |
|---|---|---|---|---|---|---|
| 1 | [juanpe500/2d_chars](https://github.com/juanpe500/2d_chars) | JavaScript (Canvas) | MIT | 2026-10, 0★ | Personagens 2D por partes | Sim: sprites renderizados em runtime |
| 2 | [MozeeB/pixel-asset-gen](https://github.com/MozeeB/pixel-asset-gen) | Python (Pillow) | MIT | 2026-04, 5★ | Sprites pixel art de vários tipos | Sim: 136 sprites, atlas e JSON |
| 3 | [princeton-vl/infinigen](https://github.com/princeton-vl/infinigen) | Python (Blender) | BSD-3-Clause | 2026-11, 7,4k★ | Mundos fotorrealistas | Sim: cenas, malhas e materiais |
| 4 | [splatterfacegames/midori](https://github.com/splatterfacegames/midori) | Rust (+ WASM, TS) | Apache-2.0 | 2026-09, 0★ | Árvores e natureza | Sim: GLB, LOD, impostores, mapas |
| 5 | [ZyFou/ProceduralTerrains](https://github.com/ZyFou/ProceduralTerrains) | JavaScript (Three.js) | MIT | 2026-11, 655★ | Terrenos | Cena em runtime |
| 6 | [elberacasa/seedbank](https://github.com/elberacasa/seedbank) | TypeScript | **Sem licença** | 2026-08, 0★ | "Assets são funções": texturas, props, sons | Sim, no navegador |
| 7 | [IceCreamYou/THREE.Terrain](https://github.com/IceCreamYou/THREE.Terrain) | JavaScript | MIT | 2026-11, 919★ | Biblioteca de terreno | Biblioteca |
| 8 | [RodZill4/material-maker](https://github.com/RodZill4/material-maker) | GDScript (Godot) | MIT | 2026-10, 6,2k★ | Materiais por grafo | Sim: mapas PBR |
| 9 | [gvastethecreator/texture-genetics](https://github.com/gvastethecreator/texture-genetics) | TypeScript (Three.js TSL/GLSL) | MIT | 2026-09, 3★ | Texturas animadas e PBR | Sim: mapas e GLB |
| 10 | [EmbarkStudios/texture-synthesis](https://github.com/EmbarkStudios/texture-synthesis) | Rust | Apache-2.0 | **Arquivado**, 2023 | Síntese por exemplo | Sim: imagens |
| 11 | [marian42/wavefunctioncollapse](https://github.com/marian42/wavefunctioncollapse) | C# (Unity) | MIT | 2021, 4,9k★ | Cidade por WFC 3D | Cena |
| 12 | [dropecho/dungen](https://github.com/dropecho/dungen) | Haxe | MIT | 2026-11, 17★ | Masmorras | Mapas (dados) |
| 13 | [Adrian104/Dungeon-Generator](https://github.com/Adrian104/Dungeon-Generator) | C++ | MIT | 2026-09, 18★ | Masmorra por BSP | Mapas (dados) |
| 14 | [dungeoncrab0606/procedural-tilemap-lab](https://github.com/dungeoncrab0606/procedural-tilemap-lab) | JavaScript | MIT | 2026-07, 0★ | Tilemaps e laboratório de material | Sim: tiles e props |

## Fichas

### 1. 2d_chars: personagem 2D por partes

- **Funcionamento [código, `sprites.js`]:**
  - A classe `SpriteRenderer` desenha um avatar por chamada.
  - O personagem é uma lista de índices: `skin`, `hair`, `shirt`, `pants`, `hairStyle`, `face`, `accessory` e `shirtPattern`, cada um aplicado como `% TABELA.length` sobre paletas e estilos.
  - A direção decide a ordem e a visibilidade das camadas: `isFacingBack` para N, NE e NW; `isLeft` e `isSide`. O "bob" da caminhada é `sin(frame*0.4)*2`.
  - Props têm dados de pose por direção (`pose_data.back_hold`, `side_hold`), `prop_rotation` e `sprite_scale`.
- **Entrada e saída:** objeto `avatar` → Canvas 2D.
- **Limites:** cada direção é desenhada por regra própria, sem fonte 3D, então a consistência entre direções depende de código manual. O estilo é Habbo.
- **Potencial:** ordem de camadas por direção e dados de empunhadura por direção (§11.2). Só como **conceito**.

### 2. pixel-asset-gen: sprites por código em Python

- **Funcionamento [código, `engine/`]:**
  - Primitivas de pixel em `drawing.py`: `draw_circle`, `draw_ellipse_filled`, `flood_fill`, `draw_outline`, `draw_outline_thick`.
  - Padrões de material: `draw_brick_pattern`, `draw_plank_pattern`, `draw_stone_texture`, `draw_thatch_pattern`.
  - `apply_shading` e `apply_shading_auto`; `dither_fill`; `composite_layers`; `create_spritesheet`.
  - Em `palette.py`: `shading_tiers(base, highlight_boost…)` com 3 níveis, `warm_shift`, `mute_color` e `recolor` por giro de matiz.
  - Em `quality.py`: `QualityProfile` com `validate_sprite_size` e `validate_atlas_size`.
- **Saída:** PNGs, atlas, JSON e uma demo no Godot com `.gd`.
- **Potencial:** confirma práticas que o PPAE já tem (rampa por material, giro de matiz, perfil de qualidade). Traz a ideia de **padrões de material nomeados** (tijolo, tábua, palha). Uso **conceitual**.

### 3. infinigen: fábricas com seed sobre o Blender

- **Funcionamento [código]:**
  - `src/infinigen/core/placement/factory.py`: classe `AssetFactory(factory_seed, coarse)`, com `FixedSeed` e `int_hash`, `create_placeholder` → `finalize_placeholders` e `asset_parameters(distance, vis_distance)`, que dá **detalhe pela distância**.
  - `core/nodes/node_wrangler.py`: classe `NodeWrangler` com `new_node`, `connect_input`, `expose_input` e `build_float_curve`. Os materiais são **grafos de nós do Blender escritos em Python**; veja `assets/objects/fruits/surfaces/apple_surface.py`, que usa TexCoord, Musgrave, Mix e RGB.
- **Saída:** cenas e malhas do Blender, com anotações para visão computacional.
- **Limites:** fotorrealismo, custo alto, cenas enormes.
- **Potencial:** **alto como arquitetura**. Fábrica com seed fixa, estágio de rascunho e estágio final, detalhe por distância, materiais como código de nós. É a mesma stack do PPAE (Blender + Python). O BSD-3 permite adaptar.

### 4. midori: árvores Weber-Penn com LOD e impostores

- **Funcionamento [código]:**
  - `crates/midori-core/src/generation.rs` traz no cabeçalho "Weber-Penn style branching algorithm", com ramificação recursiva por espécie: `BranchParams`, `TaperProfile`, `CrownShape`, `BranchRadiusModel`. Há **orçamento de geração** (`estimate_tree`, `check_estimate`, `check_mesh_stats`).
  - `tree.rs`: `Tree` → `Stem` → `Segment` → `Leaf`, com `point_at`, `direction_at` e `radius_at` ao longo do galho.
  - `leaves.rs`: `place_leaves` com distribuição ponderada por galho e `random_in_hemisphere`. Folhas em polígono, billboard ou cruz, com contorno de folha por **SDF** (`generate_leaf_outline`, `find_sdf_edge`).
  - `impostor.rs`: **rasterizador de software com z-buffer** que assa a copa vista de +Z e +X num atlas para LOD distante.
- **[doc]:** export glTF e GLB, Pivot Painter 2.0 para vento, texturas determinísticas de casca e folha, campos de solo e musgo. Seed por variante = `seed + i`.
- **Potencial:** **alto** para o futuro Nature Generator. Pode ser **incorporado como ferramenta externa** (CLI que gera GLB, depois render no nosso pipeline) ou **adaptado** (Apache-2.0).

### 5. ProceduralTerrains e 7. THREE.Terrain: terreno por campo de altura

- **[doc] THREE.Terrain:**
  - Algoritmos de altura: Cosine, Diamond-Square, Fault, Feature picking, Particle deposition, Perlin, Simplex, Value, Weierstrass e Worley.
  - Combinação de mapas (`PerlinDiamond`), suavização e `ScatterMeshes` para espalhar objetos pela geometria.
- **ProceduralTerrains [doc]:** tiles, mundo infinito e modo planeta no Three.js.
- **Potencial:** **referência conceitual** para o Environment Generator. A mistura de alturas e o espalhamento por geometria valem para qualquer linguagem.

### 6. seedbank: "um asset é uma função, não um arquivo"

- **[doc]:** cada asset é um `*.asset.ts`, ou seja, texturas em Canvas, props por geometria com seed e sons por envelope de ruído. A mesma cena é renderizada sob vários "packs" (estilos) trocando só o pacote.
- **Licença:** **não declarada**. Pela lei, isso significa todos os direitos reservados, então nada de copiar código. A ideia continua utilizável.
- **Potencial:** confirma o desenho do PPAE, em que a ficha + o gerador é a fonte e a imagem é derivada. A troca de pack equivale aos nossos perfis de arte.

### 8. Material Maker: materiais como grafo que vira GLSL

- **Funcionamento [código]:**
  - `addons/material_maker/engine/nodes/gen_base.gd`: as classes `ShaderUniform` e `ShaderCode` montam o código.
  - Cada nó contribui com declarações GLSL (`split_glsl`, `get_glsl_declaration_name`) e uniforms, que viram um shader único, compilado no Godot (`shader_compute.gd`, `pipeline/compute_shader.gd`).
- **[doc]:** a interface usa o GraphEdit do Godot.
- **Potencial:** **alto para materiais e para shaders do Godot (§4.4)**. É Godot puro e MIT. Pode ser **usado como ferramenta** para criar mapas e **estudado** para gerar `.gdshader` a partir do nosso perfil.

### 9. texture-genetics: texturas no navegador

- **[doc]:** pipeline híbrido TSL e GLSL no Three.js, padrões procedurais animados, exportação de mapas PBR e GLB. O nome sugere evolução genética de materiais ("breed materials"). **[hipótese]** Não abri o código do cruzamento.
- **Potencial:** **acompanhar**. A ideia de reproduzir e mutar parâmetros cabe no refinamento autônomo (§15.4).

### 10. texture-synthesis: síntese a partir de exemplo

- **[doc]:** *Multiresolution Stochastic Texture Synthesis*. Gera, a partir de um ou vários exemplos, uma imagem nova "parecida" (remix), com guias, preenchimento de buracos e textura que se repete sem emenda.
- **Situação:** arquivado.
- **Potencial:** baixo para o núcleo, que é geração por código. Útil só como ferramenta para variar texturas de cenário a partir de uma amostra procedural nossa.

### 11. wavefunctioncollapse (marian42): WFC 3D com retrocesso

- **[doc]:** cidade infinita montada com módulos. Cada `ModulePrototype` tem conectores, probabilidade e regras de vizinhança. A "Module data" é pré-computada e pode ser simplificada. O algoritmo usa **retrocesso** (backtracking).
- **Potencial:** **conceitual** para construções e ambientes coerentes (§8.2, §9). Licença MIT.

### 12. dungen e 13. Dungeon-Generator: masmorras

- **dungen [doc]:** autômato celular, WFC, BSP, túneis, salas, vila e caminhada aleatória.
- **Dungeon-Generator [doc]:** BSP em C++.
- **Potencial:** **conceitual** para o layout de ambientes. Sem relação com personagens.

### 14. procedural-tilemap-lab: tiles e props com luz única

- **Funcionamento [código]:**
  - `tileShading.js`: uma única luz de cena congelada (`SCENE_LIGHT = {x:-0.64, y:-0.77}`), `toneRamp(base, options)` com mistura para luz e sombra, e `ellipseLitAt`, que dá luz por normal aproximada da forma.
  - `generatedAssetAudit.js`: **auditoria dos assets gerados**, com duplicatas, órfãos, versões velhas e plano de limpeza (`auditFineGrassBakes`, `auditLegacyPropDuplicates`).
- **Potencial:** a luz única para todos os assets reforça o §3.2. A auditoria de catálogo cabe no §13.4. Uso **conceitual**.
