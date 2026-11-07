# Matriz de aderência: Master Prompt V2 (Procedural Art Engine) × estado real

**Data:** 2026-11-07. **Base:** inspeção do repositório e execução real do pipeline nesta sessão.

## Classificações

| Sigla | Significado |
|---|---|
| **IMPL** | Já mapeada e implementada |
| **MAP** | Já mapeada, não implementada |
| **PARC** | Parcialmente contemplada |
| **NÃO** | Não mapeada |

"Implementada" exige código funcionando e evidência. Documento sozinho não conta, e um teste isolado não equivale a concluído.

## Etapa 1: estado auditado

- **Repositório:** sem nenhum commit; tudo continua não rastreado e preservado. Nenhum processo do Blender ou do Godot em execução, então não há tarefa interrompida.
- **Pipeline funcionando, da ficha ao Godot:**
  - `resolve` → `build` → `rig` → `animate` → `render` (suave **ou** pixel) → `post` → `atlas` → `godot`.
  - Gates G0–G9; cache por etapa com hash de conteúdo; 52 testes.
- **Componentes:**
  - Backend: `backend/app` (CLI, contratos Pydantic, pipeline, worker do Blender, aprovações).
  - `engines/` com `character`, `rig`, `animation`, `postprocess` (inclui `pixel.py`) e `export`.
  - `blender/scripts/ics_blender` (cena, rig, animação, materiais, peças chibi, peças detalhadas, passes, sondas).
  - `integrations/godot/demo_project`.
- **Vazios:** `model_engine`, `render_engine` e `ai_engine`. Também estão vazios `backend/app/api`, `jobs` e `repositories` (sem API, fila ou banco).

## Matriz

### §2.1 Fundação gráfica

| Requisito | Class. | Componente / arquivos | Evidência | Lacuna | Próxima ação |
|---|---|---|---|---|---|
| Coordinate System | IMPL | `domain/directions.py`; doc 17 | +Z para cima, +Y frente; testes de direção; erro de 0,19 px | Só para personagens | Generalizar quando houver objeto com 1, 4 ou 8 vistas |
| Geometry Engine | PARC | `geometry.py`, `chibi_detail.fold_loft`, `master_costume.strip` | Malhas de 26 a 50 peças | Só primitivas, lofts e tiras; sem subdivisão, booleanas, curvas Bézier de superfície ou escultura | Subdivisão e deformação por campo no cabelo, no capuz e no rosto (§4.1) |
| Shape Generator | PARC | Geradores `chibi_*` | Peças por parâmetro | Formas fixas no código; poucos parâmetros expostos | Expor parâmetros de forma na ficha |
| Material System | PARC | `materials.py` (toon); `PixelMaterialRole` | 15 papéis de material no perfil pixel | Papéis presos ao perfil pixel; sem material compartilhável entre domínios | Promover os papéis a material comum a todos os acabamentos (esta etapa) |
| Procedural Texture Engine | PARC | Máscara de padrão em `stage_pixel_passes._pattern` | Costura, trama, veio e glifo | Máscara binária; sem ruído contínuo, desgaste ou mapas | Padrão contínuo no acabamento suave |
| Lighting System | IMPL | `scene.add_lights` + `ArtProfile.lights` | Luz principal e de preenchimento, pelo perfil | Um único conjunto por perfil | — |
| Shadow System | PARC | Sombra projetada nos passes; rampa toon | Capuz sombreia o rosto no pixel | Sem sombra no chão; no toon a sombra fica desligada | Sombra suave no acabamento suave; sombra no chão é opcional |
| Camera System | IMPL | `scene.add_camera`, `camera_basis` | Câmera ortográfica fixa; o root gira | — | — |
| Projection System | IMPL | `RenderProfile` | Elevação 30°, 8 direções | Só oito vistas de personagem | Perfis com 1, 2 ou 4 vistas para objetos |
| Composition Engine | PARC | `postprocess_engine/pixel.py` | Composição por passes | Só pixel | Composição suave (esta etapa) |
| Rasterization Engine | PARC | EEVEE + passes; Pillow e NumPy | Grade nativa | Sem rasterização vetorial (SVG) | Avaliar SVG para efeitos (§4.2) |
| Rendering Pipeline | IMPL | `pipeline._render`, `_render_pixel` | 3 acabamentos rodam até o Godot | — | Generalizar a etapa de composição |
| Image Processing | IMPL | `images.py`, `atlas.py`, `pixel.py` | IMG-001…005; transparência 216/216 | Atlas não recorta o quadro | Atlas recortado |
| Asset Exporter | IMPL | `export_engine/package.py`, `godot_bridge.py` | GODOT-001/002 | Sem perfil de importação do Godot (Nearest/Lossless) | Gerar `.import` conforme o acabamento |
| Quality Inspector | PARC | Gates; `scripts/master_audit_*` | Sonda de pose, transparência, prova modular | Sondas são scripts, fora dos gates; sem métrica visual | Levar as sondas para os gates (§15) |
| Asset Catalog | PARC | `library/` (assets de entrada); `projects/` | Ficha + manifesto por personagem | Sem catálogo de **saídas** (ID, seed, estado) | Catálogo de assets gerados |
| Cache System | IMPL | `pipeline._stage` + `sha256_json` | Segunda execução reaproveita | Sem cache por peça | — |

### §2.2 Geradores, §6 a §10 domínios

| Requisito | Class. | Evidência / lacuna | Próxima ação |
|---|---|---|---|
| Character Generator | PARC | Humanoide chibi com peças trocáveis e 5 variações provadas; anatomia não parametrizada (§5.1) | Continuar pelo Aprendiz |
| Creature Generator (§6) | MAP | Doc 01 §7 e roadmap Fase 7 preveem famílias; nada em código; o rig é só humanoide | Não iniciar (§17) |
| Nature Generator (§7) | NÃO | Doc 01 §6 exclui cenários do MVP | Só registrar no roadmap |
| Object Generator (§8.1) | PARC | Armas e acessórios existem como peça de personagem, não como asset solto | Futuro |
| Building Generator (§8.2) | NÃO | — | Roadmap |
| Environment Generator (§9) | NÃO | Doc 01 §6 exclui do MVP | Roadmap |
| Material Generator (§10) | PARC | Papéis de material (madeira com veio, couro com costura, metal com brilho, gema emissiva); sem pedra, terra ou água | Reusar os papéis no acabamento suave; pedra, terra e água ficam depois |

### §3 Direção artística

| Requisito | Class. | Evidência | Lacuna / próxima ação |
|---|---|---|---|
| Sistema central de direção | PARC | `ArtProfile` versionado, consumido por build, render e composição | Só personagens o consomem; a paleta mora na ficha e nos papéis |
| `pindorama_friendly_smooth_v1` | NÃO | — | **Criar nesta etapa** |
| Parâmetros centralizados (§3.2) | PARC | Luz, sombra, contorno, tons, resolução | Faltam temperatura, saturação e contraste globais e densidade de detalhes como número |
| Referências Saci e Duende (§3.3) | PARC | Duende usada como nível; Saci localizada nesta etapa | Registrar as duas em `REFERENCE_PROVENANCE.md` |

### §4 Métodos

| Requisito | Class. | Situação |
|---|---|---|
| Geometria procedural (§4.1) | PARC | Primitivas, lofts com dobras e tiras. Faltam subdivisão, campos de distância e Bézier |
| Composição vetorial (§4.2) | NÃO | Nada de SVG |
| Rasterização e processamento (§4.3) | IMPL | Pillow + NumPy + SciPy nos passes, no pixel art e nos testes |
| Shaders do Godot (§4.4) | NÃO | Nenhum `.gdshader` |
| Blender por Python (§4.5) | IMPL | Toda a construção, rig, animação e render |
| Seleção de método documentada (§4.6) | PARC | Decisões IMP-001…043; falta tabela de método por domínio |

### §5 Personagens

| Requisito | Class. | Evidência | Lacuna |
|---|---|---|---|
| Partes do corpo, rosto, olhos, cabelo, roupa, capuz, capa, botas, acessórios e armas | IMPL | Aprendiz detalhado; sonda; 3 resoluções | Sem luvas como peça própria (só braçadeiras) |
| Anatomia configurável (§5.1) | PARC | `ProportionProfile` existe no contrato, mas o chibi tem medidas fixas no código | Ligar proporção a parâmetros |
| Detalhamento automático (§5.2) | PARC | Dobras, costuras, mechas e ornamentos por código | Sem marcas de uso; detalhe é posto à mão no gerador, sem regra automática por região |
| Consistência em 8 direções (§5.3) | IMPL | Uma cena, câmera fixa, root gira; folhas das 8 direções | — |

### §11 Animação

| Requisito | Class. | Evidência | Lacuna |
|---|---|---|---|
| idle, walk, run | IMPL | ANI-001…004, GIFs, sonda | Revisão humana |
| attack, defense, cast, interaction, reactions, death, item usage | MAP | Doc 08 cita os clips; nada em código | Depois do mestre aprovado (regra 1) |
| Perfis por arma (§11.2) | PARC | Só `weapon_side` + fator de braço + compensação do antebraço | Contrato `WeaponProfile` com empunhadura e clips |
| Equipamento visual × de atributo | MAP | Doc do Pindorama: "equipamento não muda desenho" | Registrar no contrato |
| Rigs de criatura (§11.3) | MAP | — | Fase 7 |
| Animação de ambiente (§11.4) | NÃO | — | Roadmap |
| Spritesheets com pivô e metadados (§11.5) | IMPL | Atlas + manifesto + GODOT-002 | Recorte |

### §12 a §16

| Requisito | Class. | Evidência | Lacuna / próxima ação |
|---|---|---|---|
| Projeção centralizada (§12) | IMPL | `RenderProfile` + `camera_basis` | Vistas por categoria |
| Pipeline em 10 passos (§13) | PARC | Passos 1–9 para personagem | Seleção de gerador (só um) e catalogação |
| Determinismo e seed (§13.1) | PARC | Hash de ficha, perfil e código; geração sem aleatoriedade | Nenhum campo `seed`; o mesmo resultado vem por não haver acaso |
| Exportação (§13.2) | IMPL | PNG, atlas, JSON, GLB | — |
| Cache (§13.3) | IMPL | Hash por etapa (ficha, perfil, código) | — |
| Catálogo (§13.4) | PARC | Manifesto por personagem | Índice global de assets gerados |
| Offline × runtime (§14) | PARC | Tudo é offline; o Godot só toca sprites | Documentar a fronteira; nada em runtime ainda |
| Avaliação técnica (§15.1) | IMPL | Gates G1, G6, G7 e G8 + transparência | — |
| Avaliação visual (§15.2) | PARC | Folhas e comparações | Sem métrica automática de silhueta, volume ou paleta |
| Avaliação funcional (§15.3) | IMPL | Rig, animação, pivô e Godot | Oclusão de arma |
| Refinamento autônomo (§15.4) | PARC | Ciclo feito por mim (sonda → correção → nova rodada) | O software não refina sozinho |
| Pesquisa (§16) | IMPL | `RESEARCH_LOG.md` | Atualizar para o acabamento suave |
| Governança (§19) | IMPL | STATUS, DECISIONS, VALIDATION, Kanban, histórico G9 | Separar os estados (planejado → aprovado) no STATUS |

## Conflitos

| # | Decisão anterior | Novo requisito | Conflito | Justificativa e impacto | Decisão recomendada |
|---|---|---|---|---|---|
| C1 | IMP-040/041: pixel art nativo e `pindorama_pixel_art_detailed_v1`; proposta de 192 px em pixel | §1.1: "não utilizar pixel art como direção visual principal" | Direto | O pedido anterior era de pixel art. O doc 03 original já dizia "evitar aparência de pixel art" | **Manter o pixel como perfil opcional**, sem apagar. O principal passa a ser `pindorama_friendly_smooth_v1`. Os passes são reaproveitados |
| C2 | VIS-004: chibi do Mago, cerca de 2,3 cabeças | §5.1: proporções configuráveis | Parcial | O chibi segue válido como identidade, mas as medidas estão fixas no código | Manter o Aprendiz; parametrizar as proporções depois |
| C3 | D2: 3,5 cabeças | Chibi atual | Já registrado em VIS-004 | — | Revogar D2 formalmente quando o usuário aprovar |
| C4 | Doc 01 §6: cenários fora do MVP | §7 a §9: natureza, objetos, construções, ambientes | Escopo | A visão de longo prazo não muda o MVP; o §17 manda não expandir agora | Registrar como domínios futuros no roadmap; o MVP continua personagem |
| C5 | Doc 01 §2: "velocidade criativa da IA" e Fase 6 de IA | §1: geração sem IA generativa | Ênfase | A IA continua opcional e assistiva; o núcleo já roda sem IA | IA só como ferramenta opcional; Rota B (TripoSG) segue fora da produção |
| C6 | Doc 03: perfil `pindorama_stylized_v1` | §3.1: `pindorama_friendly_smooth_v1` | Nome e conteúdo | O antigo é o toon com casca 3D, reprovado no G9 | O novo é o principal; o antigo fica como histórico |

## Reutilização

- **Passes nativos** (id, luz com sombra, oclusão, padrão, profundidade): servem pixel, suave e futuros domínios.
- **Papéis de material** (pele, tecido, couro, madeira, metal, gema): viram o embrião do Material System.
- **Modelo detalhado** (`chibi_*_detail_v1`), rig, animação, exportação, gates e sondas: reaproveitados sem mudança.
