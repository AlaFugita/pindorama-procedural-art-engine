# Matriz comparativa de abordagens

**Legenda:**
- **●**: capacidade central, verificada;
- **◐**: capacidade parcial ou secundária;
- vazio: não oferece.

O PPAE aparece na última linha para comparação honesta.

| Projeto | Personagens | Criaturas | Geometria | Vegetação | Ambientes | Materiais | Texturas | Render | Iluminação | Animação | Exportação | Desempenho |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2d_chars | ● partes 2D |  |  |  |  |  | ◐ estampas | Canvas | — | ◐ bob, poses | Runtime JS | Barato |
| pixel-asset-gen | ◐ | ◐ inimigos |  | ◐ |  | ◐ padrões | ◐ | Pillow | Rampa de 3 tons | ◐ quadros | PNG, atlas, JSON | Barato |
| infinigen | ◐ (animais e humanos simples) | ● | ● nós e malhas | ● | ● | ● nós | ● | Blender | Física (Cycles) | ◐ | Blender, anotações | Muito caro |
| midori |  |  | ● ramificação | ● | ◐ solo | ◐ casca e folha | ● | Mesh + impostor | — (fora) | ◐ vento | GLB, LOD | Orçamento explícito |
| THREE.Terrain e ProceduralTerrains |  |  | ◐ grade | ◐ espalhamento | ● terreno |  |  | Three.js | Engine | — | Runtime | Rápido |
| seedbank | ◐ props |  | ◐ |  | ◐ cena | ● packs | ● Canvas | Canvas/Three | Pack | ◐ | Runtime | Barato |
| Material Maker |  |  |  |  |  | ● grafo | ● | GLSL no Godot | PBR | ◐ | Mapas PBR | GPU |
| texture-genetics |  |  |  |  |  | ● | ● animadas | TSL/GLSL | PBR | ● animadas | Mapas, GLB | GPU |
| texture-synthesis |  |  |  |  |  |  | ● por exemplo | CPU | — | — | Imagem | Médio |
| WFC (marian42) |  |  | ◐ módulos |  | ● cidade |  |  | Unity | Engine | — | Cena | Pré-cálculo |
| dungen e Dungeon-Generator |  |  |  |  | ● layout 2D |  |  | Dados | — | — | Dados | Rápido |
| procedural-tilemap-lab |  |  |  | ◐ grama | ● tiles | ◐ laboratório | ● | Canvas | Luz única | — | Pacote | Cache LRU |
| **PPAE (hoje)** | ● 3D → sprite, 8 direções, rig | | ◐ primitivas, lofts, dobras | | | ◐ papéis de material | ◐ padrão por máscara | Blender + composição | Luz do perfil + sombra projetada | ● rig + IK, 3 clips | ● atlas, JSON, GLB, Godot | Cache por etapa |

## Comparação de algoritmos

### Personagens

| Método | Quem | Consistência entre direções | Riqueza | Custo |
|---|---|---|---|---|
| Camadas 2D desenhadas por direção | 2d_chars | Depende de regra por direção | Limitada ao desenho | Mínimo |
| Pixels desenhados por código | pixel-asset-gen | Uma vista ou espelho | Limitada | Mínimo |
| **Fonte 3D com rig → render por direção → composição** | **PPAE** | **Garantida pela fonte única** | Cresce com a geometria e os materiais | Médio (offline) |

O caminho do PPAE é o único dos estudados que garante identidade nas 8 direções (§5.3). Nenhum projeto estudado oferece um método melhor para personagens.

### Vegetação

| Método | Quem | Observação |
|---|---|---|
| Weber-Penn: ramificação recursiva parametrizada por espécie | midori, infinigen | Bom para árvores de verdade; muitos parâmetros |
| L-system ou colonização de espaço | Nenhum estudado (literatura) | Colonização produz copas orgânicas; vale estudar |
| Espalhamento sobre geometria | THREE.Terrain | Distribuição, não forma |

### Terreno

Diamond-Square, Perlin, Simplex, Worley, falhas e erosão por deposição de partículas (THREE.Terrain). Combinar ruídos é o que dá variedade; nenhum algoritmo sozinho basta.

### Materiais

| Método | Quem | Prós | Contras |
|---|---|---|---|
| Grafo de nós que vira um shader | Material Maker (GLSL), infinigen (nós Blender) | Composição livre, reuso | Complexo; precisa de editor |
| Rampa de tons por material | pixel-asset-gen, tilemap-lab, PPAE | Simples, estilizado, previsível | Menos sutil |
| Síntese por exemplo | texture-synthesis | Rico a partir de amostra | Exige imagem de entrada |

Para o estilo suave do PPAE, o melhor é **rampa por material** para o tom, mais **padrões procedurais em grafo de nós do Blender**, ao estilo do NodeWrangler do infinigen, para a textura discreta.

### Composição espacial

| Método | Quem | Melhor para |
|---|---|---|
| WFC com retrocesso | marian42, dungen | Estruturas modulares coerentes (cidade, interiores) |
| BSP | Dungeon-Generator, dungen | Salas e corredores |
| Autômato celular | dungen | Cavernas e manchas orgânicas |
