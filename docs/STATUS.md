# Estado real do produto

**Atualizado em:** 2026-11-07  
**Resumo:** a cadeia técnica funciona de ponta a ponta. A qualidade artística foi **reprovada** pelo usuário. Novas animações, famílias e UI estão congeladas até aprovar um personagem mestre.

Auditoria: [audit/AUDITORIA_VISUAL_2026-11-06.md](audit/AUDITORIA_VISUAL_2026-11-06.md)

## Auditoria do mestre e sistema de detalhamento, 2026-11-07

| Item | Estado | Evidência |
|---|---|---|
| Auditoria final do Aprendiz (6 itens) | Feita; correções pontuais aplicadas; **G9 aguarda o usuário** | [AUDITORIA_MESTRE_APRENDIZ_2026-11-07.md](audit/AUDITORIA_MESTRE_APRENDIZ_2026-11-07.md) |
| Personalização modular | Testada: 5 variações de um campo cada | `audit/master_audit/modular/` |
| Transparência | Pixel art 216/216; o suave tem franja clara na borda creme | `audit/*/transparencia/` |
| Pixel art nativo + perfil detalhado | Implementado e testado até o Godot; **arte aguarda o usuário** | [DETALHAMENTO_ARTISTICO.md](DETALHAMENTO_ARTISTICO.md) |
| Resolução 128, 192, 256 | Medida; proposta de 192, não decidida | `audit/detalhamento/resolucao/` |
| Testes automatizados | 52 passam | `pytest` |

## Personagem chibi, 2026-11-07

Novo caminho decidido em [VIS-004](DECISIONS.md), com análise em [ANALISE_ALVO_CHIBI_2026-11-07.md](audit/ANALISE_ALVO_CHIBI_2026-11-07.md).

| Item | Estado | Evidência |
|---|---|---|
| Aprendiz e Aprendiz da Floresta | Cadeia testada; **arte aguarda o usuário** | G1, G7 e G8 PASS; G3, G4, G5 e G9 REVIEW; G6 WARN |
| Animação idle, walk, run | Testada por métrica; **sem revisão humana** | Na caminhada: IK 0,00001 H, foot sliding 0,00002 H/s, loop 0 |
| Godot | Testado | 24 clips, 192 frames, 48 telas iguais |
| Testes automatizados | 47 passam | `pytest` |

Aviso aberto: IMG-005, 2 frames repetidos no idle, porque o movimento é pequeno a 128 px.

Defeitos que ainda vejo: borda do capuz aparece de leve nas vistas de costas, riscos pequenos ao lado dos olhos, e o traço liso difere do Mago pixelado. Evidência: [comparação](audit/chibi/comparacao_mago.png) e [sprites](audit/chibi/sprites_final.png).

## Cadeia técnica e histórico

| Área | Estado | Evidência / observação |
|---|---|---|
| Ambiente (Blender 5.2.3, Godot 4.7.2) | Testado | `ics doctor`; [ENVIRONMENT_REPORT.md](ENVIRONMENT_REPORT.md) |
| Contratos e JSON Schema | Testado | `tests/unit`, `schemas/` |
| DirectionConvention e projeção | Testado | erro máximo de 0,19 px |
| Worker Blender | Testado | timeout, falha, caminho com espaço e acento |
| Rig semântico | Testado | RIG-001…004; **revisão humana pendente** |
| idle, walk, run | Testado | ANI-001…004; **revisão humana pendente** |
| Render de oito direções | Testado | 192 frames, IMG-001/003/004 |
| Exportação e manifesto | Testado | EXP-001/002 |
| Godot | Testado | GODOT-001/002; revisão humana pendente |
| Cache por etapa | Testado manualmente | segunda execução reaproveitou todas as etapas |
| Biblioteca de arte procedural | **Reprovada** | G9 `REJECTED` |
| Vídeo do Godot | Implementado, não executado | `record_video` nunca rodou |
| CA-003 três variações | Pendente | só o Guardião foi executado |
| CA-011 falha simulada | Implementado, não testado | gancho `fail_at` existe, sem teste |
| Golden images e regressão | Pendente | sem baseline aprovado |
| API FastAPI, SQLite, fila | Pendente | |
| App Tauri/React | Pendente | congelado |
| IA | Pendente | `ai_engine` vazio |

**Pacote atual:** `exports/guardiao_da_floresta`, release `experimental`, aprovação `UNAPPROVED`.

## Character Master Prototype

Relatório: [MASTER_PROTOTYPE_REPORT.md](MASTER_PROTOTYPE_REPORT.md)

| Item | Estado | Evidência |
|---|---|---|
| Rota A, quatro vistas em argila | Implementado, **sem aprovação** | `docs/audit/master_prototype/` |
| Proporção de 3,5 cabeças | Testado | 3,51 medidas; perfil versionado |
| Rosto e cabelo da Rota A | **Reprovados pelo agente** | close e lado a lado |
| Rigging da Rota A | Testado em pose extrema | problemas no peito e na ombreira |
| Rota B (TripoSG) | Testada localmente, **sem aprovação** | identidade forte; ~4,5 cabeças, malha fundida; `t03` |
| Rota C (híbrida) | **Aprovada como forma base** (G3M, usuário) | `t09`; não é arte final; G9 segue `REJECTED` |
| Teste de textura | Testado, sem aprovação | `paint/t03`: cabeça com identidade; corpo chapado |
| Pintura do corpo | **Reprovada pelo usuário** em 2026-11-07: caminho divergente do desejado | `paint/t05`: lê como personagem de jogo nas quatro vistas; pendências no relatório |
| Gate G3M | Base aprovada pelo usuário; bloqueio automático no pipeline ainda não implementado | [MASTER_QUALITY_CRITERIA.md](MASTER_QUALITY_CRITERIA.md) |
| Decisões D1–D6 | Registradas | [DECISIONS.md](DECISIONS.md), [REFERENCE_PROVENANCE.md](REFERENCE_PROVENANCE.md) |

## Próximo incremento

Trabalho pausado: alinhar com o usuário o resultado esperado antes de qualquer nova rodada. Ver [MASTER_PROTOTYPE_REPORT.md](MASTER_PROTOTYPE_REPORT.md).
