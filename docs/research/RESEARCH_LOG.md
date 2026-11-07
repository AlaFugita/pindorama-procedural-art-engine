# Registro de pesquisa

Consulta em 2026-11-06. "Blog" indica fonte secundária, que nunca fundamentou decisão sozinha.

| Pergunta | Fonte | Versão | Conclusão | Decisão / código |
|---|---|---|---|---|
| Versão LTS atual do Blender? | https://www.blender.org/download/lts/ , https://download.blender.org/release/Blender5.2/ | 5.2.3 (22/10/2026) | LTS vigente; checksum oficial publicado | IMP-003 |
| API Python mudou no 5.x? | https://developer.blender.org/docs/release_notes/5.0/python_api/ | 5.0+ | `media_type` antes de `file_format`; motor `BLENDER_EEVEE`; `action.fcurves` removido | `scene.py`, `animation.py` |
| Flags de linha de comando | `blender --help` executado | 5.2.3 | `--background`, `--factory-startup`, `--python-exit-code` | `blender_worker.py` |
| Bones e armature | https://docs.blender.org/api/current/info_gotchas_armatures_and_bones.html | 5.2 | Página longa truncada pela ferramenta; comportamento validado por execução | `rig.py`, testes |
| SpriteFrames | https://docs.godotengine.org/en/stable/classes/class_spriteframes.html | 4.7 | `set_animation_loop` obsoleto; usar `set_animation_loop_mode` | `ics_character.gd` |
| CLI Godot | https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html | 4.7 | `--headless --import`, `--script`, `--write-movie` | `godot_bridge.py` |
| TRELLIS.2 | https://github.com/microsoft/TRELLIS.2 | jul/2026 | MIT; 24 GB; só Linux testado | Não cabe localmente |
| Hunyuan3D 2.0 | https://github.com/Tencent-Hunyuan/Hunyuan3D-2 , https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE | 2.0 | 6 GB forma, 16 GB total; Windows; exclui UE/UK/Coreia; 1M MAU; saídas sem reivindicação da Tencent | Candidato a rascunho, sujeito a D4 |
| Hunyuan3D 2.1 | https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1 | 2.1 | 10 GB forma; 29 GB total | Descartado localmente |
| UniRig | https://github.com/VAST-AI-Research/UniRig | jun/2026 | Código MIT; pesos sem licença declarada; 8 GB; sem garantia de nomes | Reserva |
| CharacterGen | GitHub API `zjp-shadow/CharacterGen` , arXiv 2402.17214 | — | Apache-2.0 no código; base VRoid | Não usar em produção |
| StdGEN | https://github.com/hyz317/StdGEN | abr/2026 | Checkpoints só para pesquisa | Não usar em produção |
| QRemeshify | https://github.com/Ksami/QRemeshify | 2024 | GPL-3.0; add-on sem executável externo | Ferramenta de retopologia |
| Instant Meshes | GitHub API `wjakob/instant-meshes` | 2022 | Licença não normalizada pela API; precisa de leitura | Sem decisão |
| StableGen | https://github.com/sakalond/StableGen | nov/2026 | GPL-3.0; ~8 GB com SDXL; Blender 5.1+; bake em UV; alguns modelos não comerciais | Testes de textura |
| ComfyUI | GitHub API `Comfy-Org/ComfyUI` | nov/2026 | GPL-3.0 | Backend opcional |
| Base CC0 | https://www.blender.org/download/demo-files/ , https://studio.blender.org/training/stylized-character-workflow/base-meshes/ | v1.4.1 | CC0; 49 MB; quad, UDIM, volumes fechados | Rota A |
| Fluxo estilizado | https://studio.blender.org/training/stylized-character-workflow/base-meshes/ | — | Escultura, retopo, UV, textura, shading, bake | Arquitetura do mestre |
| Rigify | https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/addons/rigify/introduction.rst | manual | Não faz skinning | Manter rig próprio |
| Quaternius | https://quaternius.com/packs/universalbasecharacters.html | — | Página indica CC0; blog cita QAL | Conferir por pack |
| Meshy | https://www.meshy.ai/terms-of-use , https://docs.meshy.ai/pricing | nov/2026 | Pago é dono da saída; gratuito CC BY; treino salvo opt-out | Opção sujeita a D4/D5 |
| Tripo | https://www.tripo3d.ai/terms | — | **HTTP 403: termos não lidos** | Sem decisão |
| Mixamo | Adobe Additional Terms PDF (2021) | — | PDF ilegível pela ferramenta | Sem decisão |
| NPR | https://www.cgchannel.com/2024/12/check-out-blenders-experimental-non-photorealistic-rendering-build/ (blog) | — | Goo em 4.1; branch experimental | Rejeitado |

## Character Master Prototype (2026-11-06)

| Pergunta | Fonte | Versão | Conclusão | Decisão / código |
|---|---|---|---|---|
| O que há na base CC0? | Inspeção do `.blend` (mirror.blender.org/demo/asset-bundles/human-base-meshes/) | v1.4.1 | Corpo estilizado de 12.502 vértices, fechado, simétrico, com UV | Rota A |
| Pesos do TripoSG | https://huggingface.co/api/models/VAST-AI/TripoSG | commit 2c1c516 | MIT, safetensors, 7,4 GiB | IMP-016 |
| Requisitos do TripoSG | https://github.com/VAST-AI-Research/TripoSG | commit fc5c409 | 8 GB; usa RMBG-1.4 e `diso` | IMP-017, IMP-018 |
| RMBG-1.4 | https://huggingface.co/briaai/RMBG-1.4 | 1.4 | Não comercial sem acordo | Não baixado |
| TRELLIS | https://github.com/microsoft/TRELLIS | out/2026 | MIT, 16 GB, Linux | Fora |
| TripoSR | https://huggingface.co/api/models/stabilityai/TripoSR | — | MIT; `.ckpt` | Reserva |
| Termos da OpenAI | https://openai.com/policies/row-terms-of-use/ (via busca; página direta HTTP 403) | nov/2026 | Saída do usuário na medida da lei; pode não ser única | D1 |
| Patamares no TripoSG | Execução local e leitura de `autoencoder_kl_triposg.py` | commit fc5c409, torch 2.11 | float16 + caminho rápido: 30,4% faces alinhadas; float32 + hierárquico: 0,8% | IMP-025 |

## 2026-11-07: alvo chibi

Fontes locais do Pindorama: `DIRECAO-DE-ARTE.md`, `ADR-0013`, `mago_referencia_jogo.png`. Sem pesquisa externa. Achado técnico: em EEVEE, a casca de contorno por Solidify projeta sombra sobre a malha e apaga o tom claro do toon; resolvido com `light_shadows` falso no perfil chibi.

## 2026-11-07: detalhamento e pixel art

- Blender, Shader to RGB: só no EEVEE e quebra AO e sombras de contato. Por isso a oclusão vai num canal separado (nó AO) e não passa pela rampa. https://docs.blender.org/manual/en/4.0/render/shader_nodes/converter/shader_to_rgb.html
- 3D para pixel art: render em baixa resolução, paleta por pixel e contorno por salto de profundidade e normal; antialiasing estraga contorno e cluster. https://medium.com/@elliotbentine/pixelizing-3d-objects-b55ec33328f1
- Pixel art: contorno seletivo (sel-out), giro de matiz nas sombras, evitar pixels órfãos. https://lospec.com/articles/pixel-art-outlines-part-2-using-color e https://pixnote.net/en/learn/shading
- Godot 4: pixel art sem compressão VRAM e com filtro Nearest no CanvasItem ou no padrão do projeto. https://docs.godotengine.org/en/4.5/tutorials/assets_pipeline/importing_images.html
- IA de textura local e aberta: nada maduro encontrado. Material Maker é procedural e citado como MIT (verificar o LICENSE antes de usar). Nenhuma imagem foi enviada para fora.

