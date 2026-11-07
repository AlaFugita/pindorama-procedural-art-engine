# Decisões técnicas

Formato: contexto, escolha, motivo, consequência. Responsável: agente, salvo indicação. Data: 2026-11-06.

| ID | Tema | Escolha | Motivo | Consequência | Estado |
|---|---|---|---|---|---|
| IMP-001 | Raiz do repositório | Código na pasta dos documentos, sem mover nada | Preserva o pacote; difere do `isometric-character-studio/` do doc 10 | Documentos ficam na raiz; `docs/` guarda registros vivos | Aprovada pelo agente |
| IMP-002 | pyproject | Um só na raiz, sem `backend/pyproject.toml` | Um pacote instalável basta; doc 10 sugeria dois | Simplifica `uv` e testes | Aprovada pelo agente |
| IMP-003 | Blender | Portátil 5.2.3 LTS em `tools/`, fora do Git | Suporte até jul/2028; não altera o sistema; DA-007 segue aberta para o instalador | `ICS_BLENDER` permite outro caminho | Autorizada pelo usuário |
| IMP-004 | Godot | 4.7.2 a partir do zip já baixado pelo usuário | Evita novo download | `ICS_GODOT` permite outro caminho | Aprovada pelo agente |
| IMP-005 | DA-002 projeção | Ortográfica, elevação de 30° | Produz losango 2:1 no chão | Configurável em `RenderProfile` | Proposta: falta teste com cenário do jogo |
| IMP-006 | DA-003 rotação | Câmera fixa ao sul; o root gira | Luz coerente com a câmera; doc 18 §4 | Sombra projetada não é renderizada | Aprovada pelo agente |
| IMP-007 | DA-001 resolução | 256×320 a 160 px/m, pivot (128, 284) | Comporta lança e corrida com margem | Revisar para o novo personagem | Proposta |
| IMP-008 | DA-004 atlas | Uma tira por animação e direção, gutter de 2 px | Carregamento seletivo; depuração simples | 24 PNGs por personagem | Aprovada pelo agente |
| IMP-009 | DA-005 clips | idle 8f@8, walk 8f@12, run 8f@16 | Ciclo limpo; contatos exatos em frames | Configurável por clip | Proposta: revisão humana |
| IMP-010 | Pesos | Distância a segmentos com filtro de lado, sem Bone Heat | Determinístico e sem cruzar esquerda/direita | Pesos simples; rever na malha real | Provisória |
| IMP-011 | Animação | Em esteira (`in_place`), pés por IK, rotação do pé via alvo | Foot sliding mensurável contra `ground_speed_mps` | Movimento em world é do jogo | Aprovada pelo agente |
| IMP-012 | Estrutura de export | Sem pasta `animations/`; atlases, metadata, qa e source | Atlas é a saída primária; doc 09 permite ajuste | Documentado aqui e coberto por EXP-001 | Aprovada pelo agente |
| IMP-013 | Cache | Pasta de etapa por hash de entradas + código | Regeneração seletiva sem regras na UI | Alterar script Blender invalida tudo | Aprovada pelo agente |
| IMP-014 | Escala do corpo | Apenas 1,0 no MVP | Rig e passada não escalam ainda | G1 rejeita outro valor | Limitação |
| IMP-015 | Biblioteca procedural | Assets originais por código | Prova da cadeia sem licenças de terceiros | **Reprovada como arte**; rebaixar a fixture | Substituída (ver VIS-001) |
| VIS-001 | Qualidade visual | Aprovar personagem mestre antes de animar | Decisão do usuário: a arte atual está reprovada | Ver auditoria; G3M proposto | **Decisão do usuário**; detalhes pendentes |

## Divergências entre documentos

- O doc 10 propõe `backend/pyproject.toml`; adotou-se um único na raiz (IMP-002).
- O doc 09 §3 lista `animations/`; o pacote não a inclui (IMP-012).

## Decisões oficiais do usuário (2026-11-06)

| ID | Decisão | Consequência |
|---|---|---|
| D1 | Referência gerada pelo ChatGPT ImageGen; não é modelo 3D nem referência geométrica perfeita | [REFERENCE_PROVENANCE.md](REFERENCE_PROVENANCE.md) |
| D2 | 3,5 cabeças como proporção canônica do jogável | Perfil `library/profiles/proportions/humanoid_35h_v1.json`, contrato `ProportionProfile` |
| D3 | Fantasia original; sem representar comunidade específica; sem misturar culturas reais sem pesquisa e revisão | Regra permanente de arte |
| D4 | Nada do projeto vai a serviço externo sem autorização expressa; Hunyuan3D 2.0 fora de produção | Rota B só local |
| D5 | Sem serviços pagos nem infraestrutura nesta etapa | Sem nuvem |
| D6 | Protótipo sem equipamentos adicionais | Arco, aljava, lança e faca removidos |

Regras de aprovação 1 a 8: [MASTER_QUALITY_CRITERIA.md](MASTER_QUALITY_CRITERIA.md).

## Decisões técnicas do protótipo

| ID | Tema | Escolha | Motivo | Consequência | Estado |
|---|---|---|---|---|---|
| IMP-016 | Rota B | TripoSG local | Único com código e pesos MIT, safetensors e 8 GB | Testado no protótipo; **não incorporado à produção** (regra 4) | Experimental |
| IMP-017 | Máscara da Rota B | Código próprio em vez de RMBG-1.4 | RMBG-1.4 é não comercial | `scripts/route_b_prepare.py` | Aprovada pelo agente |
| IMP-018 | diso | Trocar por marching cubes do scikit-image, com NaN preenchido por sinal | `diso` exige compilação CUDA | Executado; o caminho final (hierárquico) nem usa `diso` | Experimental |
| IMP-019 | Ambiente da Rota B | Python 3.12 isolado em `tools/route_b` | uv falhou com Python 3.10 no Windows; não contamina o projeto | README pede 3.10: compatibilidade a provar | Proposta |
| IMP-020 | Estúdio de argila | Workbench, sem textura e sem sombra | Comparação honesta da forma | `stage_master_clay` | Aprovada pelo agente |
| IMP-021 | Proporção Rota A | Remapear segmentos do esqueleto | Preserva quads e UV | Topologia estabilizada | Aprovada pelo agente |
| IMP-022 | Peças da roupa | Construídas sobre a superfície real do corpo | Evita raio paramétrico | Reconstrução ao mudar o corpo | Provisória |
| IMP-023 | Histórico de aprovações | `approvals.json` com lista `history` | Regra 6; antes sobrescrevia | Testado | Aprovada pelo agente |
| IMP-025 | Decodificador TripoSG | float32 + caminho hierárquico | float16 no caminho rápido gerou patamares | Combinação validada; causa não isolada | Experimental |
| IMP-024 | Gate G3M | Registrado em critérios e CLI | Antes de G4/G5 | **Bloqueio automático no pipeline ainda não implementado** | Pendente |
| IMP-026 | Rota C | Base CC0 projetada sobre a B, com relaxamento e projeção alternados | Preserva quads e UV; reaproveita forma | `stage_master_c`; parâmetros valem para esta geração | Experimental |
| IMP-027 | Limite de iteração | Parar após regressão (t04) e registrar defeitos | Ajustes passaram a trocar um defeito por outro | Decisão humana antes de novos ajustes | Aprovada pelo agente |
| IMP-028 | Máscara da Rota B | Contorno traçado protege a pluma; arco e aljava seguem a borda do corpo | Cortes retos viraram placas planas | `scripts/route_b_prepare.py`; resultado confirmado em `route_b/t04` | Aprovada pelo agente |
| IMP-029 | Boca da Rota C | Remendo pequeno com a superfície da B | Interior da base fica com faces invertidas | Costura leve; resolver na retopologia | Provisória |
| IMP-030 | Transplante por recorte | Desligado (`transplant`) | t07 falhou: ornamentos da B estão fundidos à pele | Peças finais exigem outra técnica | Aprovada pelo agente |
| IMP-031 | Continuidade autônoma | Usuário delegou a decisão técnica; parar na t09 para revisão humana | Regra 3: nenhuma aprovação artística automática | G3M pendente | Delegada pelo usuário |
| VIS-002 | Forma base | Rota C t09 aprovada só como base | **Decisão do usuário**, 2026-11-07 | Textura liberada para teste; arte final segue pendente | **Decisão do usuário** |
| IMP-032 | Teste de textura | Projeção só na cabeça + cor por peça, em cor por vértice | Projeção no corpo falhou: pose da B difere da prancha | Local, sem custo; não é textura final | Experimental |
| IMP-033 | Sonda de sprite por região | `stage_master_probe`, separado de `stage_master_paint` | Executada sem conhecer `paint/t03`; autorizada pelo usuário; arquivo da outra sessão foi sobrescrito e restaurado do histórico | Só evidência; não substitui `paint/t03` | Encerrada |
| IMP-034 | Pintura do corpo | Cor por vértice com curvatura e inclinação vertical; grafismos por coordenadas | Luz pintada independe do giro; sem imagem de terceiros | Protótipo; produção exige UV e textura | Experimental |
| VIS-003 | Pintura paint/t05 | Reprovada pelo usuário: caminho diferente do que deveria | **Decisão do usuário**, 2026-11-07 | Trabalho pausado até alinhar o resultado esperado | **Decisão do usuário** |
| VIS-004 | Alvo visual | **Chibi na linha do Mago**, cerca de 2,3 cabeças, desenho liso, sensação de Ragnarok Online. Substitui D2 neste caminho | Decisão do agente por delegação do usuário, 2026-11-07. Motivo: [audit/ANALISE_ALVO_CHIBI_2026-11-07.md](audit/ANALISE_ALVO_CHIBI_2026-11-07.md) | Aprovação artística segue com o usuário; liso ou pixel segue aberto | Provisória |
| IMP-035 | Família chibi | Rig, animação, render e arte próprios, peças por código e `light_shadows` falso no perfil | A casca do contorno sombreava o corpo e apagava o tom claro | Perfis antigos mantêm o comportamento | Aprovada pelo agente |
| IMP-036 | Mão da arma | `weapon_side` vem da âncora da arma | O Mago segura o cajado na mão esquerda | Padrão continua na direita | Aprovada pelo agente |
| IMP-037 | Sonda de pose | `stage_audit_pose`: chão por peça e coxa × túnica por seção real do tecido | Os gates mediam ossos, não a malha; a primeira versão por fatias deu falso positivo | Achou botas −2,3 mm, cajado −23,7 mm e coxa 30 mm na corrida; todos corrigidos | Aprovada pelo agente |
| IMP-038 | Mão da arma | Antebraço compensa o balanço do braço (`6 − 0,7 × balanço`) | Cajado herdava a dobra do antebraço e virava lança na corrida | Vale para todo personagem com arma | Aprovada pelo agente |
| IMP-039 | Prova modular | `mesh_sha` por peça no build | Mostrar que a troca de um campo só muda as peças do componente | 5 variações; perfis idênticos | Aprovada pelo agente |
| IMP-040 | Pixel art | Passes nativos (id, luz com sombra, profundidade) + composição por regra; alpha binário | Pedido de não reduzir resolução por filtro; anti-aliasing quebra cluster e contorno | `ArtProfile.pixel` opcional; ramo `_render_pixel` | Provisória |
| IMP-041 | Perfil `pindorama_pixel_art_detailed_v1` | Rampas por material com giro de matiz, contorno seletivo externo, linhas por profundidade | Diagnóstico em [DETALHAMENTO_ARTISTICO.md](DETALHAMENTO_ARTISTICO.md) | Estilo do MMORPG **não** fixado | Aguarda usuário |
| IMP-042 | Modelo detalhado | Assets `chibi_*_detail_v1` ao lado dos anteriores | Evoluir sem descartar o protótipo | Mesmo rig e animação | Aguarda usuário |
| IMP-043 | Resolução de referência | **Proposta:** 192 px, com atlas recortado | 192 lê bem; 256 custa 1,8× a memória com ganho pequeno | Atlas recortado ainda não existe | Proposta |
| VIS-005 | Direção visual principal | **Ilustração suave** (`pindorama_friendly_smooth_v1`); pixel art passa a opcional | Requisito do usuário, Master Prompt V2, 2026-11-07 | Conflito C1: IMP-040/041 continuam válidos como perfil opcional | Decisão do usuário |
| ARC-001 | Procedural Art Engine | Visão de longo prazo incorporada aos docs 01, 03, 04, 11 e 13, sem módulos novos por item | Master Prompt V2 §0 e §2.1 | [Matriz](audit/MATRIZ_ADERENCIA_PROCEDURAL_ART_ENGINE_2026-11-07.md) | Aprovada pelo agente |
| ARC-002 | Acabamentos como ramos | toon, pixel e smooth consomem os mesmos passes | Evita duplicar render e composição | `ArtProfile` escolhe o ramo | Aprovada pelo agente |
| LIC-001 | Licenças | Projeto **pessoal, de hobby, nunca comercializado**: pode usar recursos prontos e imagens de outros jogos como referência ou apoio quando ajudar | Decisão do usuário, 2026-11-07 | Afrouxa a regra 4 e D4 para licença; a identidade visual continua própria e a geração principal continua por código | Decisão do usuário |
| PUB-001 | Publicação | Repositório público no GitHub + GitHub Pages | Pedido do usuário, 2026-11-07; Pages gratuito exige repositório público | Autoriza enviar o projeto ao GitHub (supera D4 para este destino) | Decisão do usuário |
| IMP-044 | Acabamento suave | `engines/postprocess_engine/smooth.py`: passes em 3×, tom contínuo por material, contorno de espessura variável, linhas internas finas, brilho difuso, redução com alpha pré-multiplicado | Master Prompt V2 §1.1 e §3.1 | `ArtProfile.smooth`; ramo `_render_composed` | Aprovada pelo agente; arte aguarda o usuário |
| IMP-045 | Luz de borda e textura contínua | Rim pela normal de tela da silhueta; ruído de baixa frequência no canal G do passe de profundidade | Experimentos E1 e E2 da pesquisa | Sem passe extra de render | Aprovada pelo agente |
| IMP-046 | Faixa bordada no capuz | Anel dourado com contas paralelo à abertura | Aproximar do nível de detalhe da Duende | Só no `chibi_robe_detail_v1` | Aguarda usuário |
| IMP-047 | Rosto | **Decalque vetorial procedural** (`face_decal.py`): formas 2D no plano do rosto, presas à superfície da cabeça, projetadas por quadro com a matriz da cabeça e mascaradas pelos pixels da cabeça | Feedback do usuário: "o rosto não está ficando bom; não precisa ser realista". Peças 3D finas brigavam com sombra, franja e espessura | `chibi_face_decal_v1`; G3 aceita componente sem malha (`NON_MESH_GENERATORS`) | Aguarda usuário |
| IMP-048 | `seed` na ficha | `CharacterSpec.seed` (padrão 0) varia as mechas de forma reproduzível | Recomendação P1 da pesquisa (F1) | Entra no hash da ficha | Aprovada pelo agente |
| IMP-049 | Mechas por curva | Bézier com conicidade e ponta curvada | Recomendação P1 (F4, ideia do midori) | Franja acima das sobrancelhas; peças finas sem sombra projetada | Aprovada pelo agente |
| IMP-050 | Atlas recortado | `RenderProfile.atlas_trim`: caixa justa por quadro + `ox`/`oy`; o Godot reconstrói o quadro com `AtlasTexture.margin` | Recomendação P1; memória do MMORPG | 192 px: VRAM de 27,9 para **10,6 MiB** por personagem; GODOT-001/002 PASS | Aprovada pelo agente |
| IMP-051 | Pivô inteiro | Perfis `isometric_smooth_*` com pivô arredondado | Meio pixel (160,5) deslocava a região recortada no Godot e reprovava o GODOT-002 | Perfis antigos mantidos | Aprovada pelo agente |

