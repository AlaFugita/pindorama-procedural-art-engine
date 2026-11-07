# Relatório de validação

**Execução:** 2026-11-06, Windows 11, Blender 5.2.3, Godot 4.7.2.  
**Decisão de liberação:** **não liberado.** Release `experimental`: G9 `REJECTED` e G2 sem aprovação.

## Comandos executados

```bash
uv run pytest -q
uv run ics doctor
uv run ics run tests/fixtures/specs/guardiao_da_floresta.json
uv run python scripts/audit_visual.py <referencia> docs/audit/evidence
```

Resultado do pytest: 42 aprovados. Evidências das etapas em `projects/default/characters/guardiao_da_floresta/gates/`.

## Matriz (doc 23)

| ID | Resultado | Observação |
|---|---|---|
| ENV-001 | PASS | versões suportadas pelo `ics doctor` |
| SPEC-001 / 002 | PASS | campos e referências ausentes rejeitados |
| BL-001 / 002 | PASS | inclui caminho com espaço e acento |
| RND-001 | PASS | PNG RGBA 256×320 |
| RND-002 | REVIEW | largura medida correta; falta revisão |
| RIG-001 | PASS | 33 ossos |
| RIG-002 | PASS + REVIEW | 6 poses; folha aguarda pessoa |
| RIG-003 | PASS | 5 marcadores, 8 direções, 0,19 px |
| RIG-004 | PASS + REVIEW | bind 0,00 mm; deformação aguarda pessoa |
| ANI-001…004 | PASS + REVIEW | idle, walk e run |
| DIR-001 / 002 | PASS | direções distintas, sem espelhamento |
| IMG-001 / 003 / 004 | PASS | |
| IMG-002 | WARN | caixa do idle varia até 8 px |
| EXP-001 / 002 | PASS | |
| GODOT-001 | PASS | 24 clips, 192 frames, pixels idênticos |
| GODOT-002 | PASS + REVIEW | 48 telas conferidas; falta pessoa |
| ART-001 | **NOT_TESTED** | sem conceito aprovado (G2) |
| ART-002 | **REJECTED** | reprovado pelo usuário |
| Vídeo Godot, CA-003, CA-011, golden | **NOT_TESTED** | |

Contagem: G1, G7, G8 `PASS`; G3, G4, G5 `REVIEW`; G6 `WARN`; G2 sem aprovação; G9 `REJECTED`.

## Defeitos reais encontrados pelas validações

1. **Joelhos invertidos.** `pole_angle` com sinal errado dobrava o joelho para trás. Contato e foot sliding passavam mesmo assim. Corrigido, com checagem de bind e de joelho em todo frame.
2. **Caminho relativo no worker.** Falhava porque o Blender roda com `cwd` no diretório de trabalho. Corrigido em `run_stage`.

## Lacuna da própria matriz

Todos os testes acima medem integridade. **Nenhum mede qualidade artística.** Passar neles não contradiz a reprovação visual. A auditoria propõe o gate G3M e os testes VIS.

## Character Master Prototype (2026-11-06)

Comandos: `python scripts/master_prototype.py a t08`, `python scripts/master_metrics.py t08 <mascara>`, `uv run pytest -q`.

| ID | Rota A (t08) | Rota B |
|---|---|---|
| MST-T1 proporção | PASS: 3,51 | **FAIL:** ~4,5 (estimativa) |
| MST-T2 corpo fechado | PASS: 0 aberta, 0 não-manifold | PASS parcial: 0 aberta, mas 42 componentes |
| MST-T3 quads | PASS: corpo 100%; total 98,8% | **FAIL:** 0 quads |
| MST-T4 mesmo arquivo | PASS: um `.blend` | PASS: um `.blend` |
| MST-T5 licença | PASS: CC0 + código próprio | REVIEW: MIT declarado; pendências no relatório |
| MST-V1…V7 | REVIEW: pendente de pessoa; agente indica reprova em V2, V3 e V6 | REVIEW: pendente de pessoa; agente indica defeitos nas costas |
| MST-F1 rig semântico | NOT_TESTED: só rig simples | NOT_TESTED: só rig simples |
| MST-F2 pose extrema | FAIL parcial: sem NaN, mas ombreira solta | FAIL parcial: sem NaN, mas saia rasga |
| MST-F3 alongamento | FAIL: p99 1,60× (meta 1,5×) | FAIL: p99 5,32× |
| MST-F4 peças removíveis | PASS: 30 objetos | **FAIL:** malha fundida |

G9 anterior: permanece `REJECTED`. G3M: não aprovado.

### Rota C (t05, 2026-11-07)

| ID | Resultado |
|---|---|
| MST-T1 proporção | PASS: 3,51 |
| MST-T2 corpo fechado | PASS: corpo 0 aberta, 0 não-manifold; cabelo aberto, 3 arestas não-manifold |
| MST-T3 quads | PASS no corpo; cabelo em triângulos |
| MST-T4 mesmo arquivo | PASS |
| MST-T5 licença | REVIEW: herda pendências da Rota B |
| MST-V1…V7 | REVIEW: pendente de pessoa; agente indica defeitos em V2, V3 e V7 |
| MST-F1 rig semântico | NOT_TESTED: só rig simples |
| MST-F2 pose extrema | FAIL parcial: sem NaN, ombreira solta |
| MST-F3 alongamento | FAIL: p99 1,52× (meta 1,5×) |
| MST-F4 peças removíveis | PASS: 24 objetos |

### Rota C (t06, 2026-11-07, entrada refeita)

| ID | Resultado |
|---|---|
| MST-T1 proporção | PASS: 3,49 |
| MST-T2 corpo fechado | PASS no corpo; cabelo aberto, 1 aresta não-manifold |
| MST-T3 quads | PASS no corpo; cabelo em triângulos |
| MST-T5 licença | REVIEW: herda pendências da Rota B |
| MST-V1…V7 | REVIEW: pendente de pessoa |
| MST-F1 rig semântico | NOT_TESTED |
| MST-F2 pose extrema | FAIL parcial: sem NaN, ombreira solta |
| MST-F3 alongamento | FAIL: p99 1,52× (meta 1,5×) |
| MST-F4 peças removíveis | PASS: 24 objetos |

### Rota C (t09, 2026-11-07, candidata)

| ID | Resultado |
|---|---|
| MST-T1 proporção | PASS: 3,49 |
| MST-T3 quads | PASS no corpo; cabelo em triângulos |
| MST-V1…V7 | REVIEW: pendente de pessoa |
| MST-F1 rig semântico | NOT_TESTED |
| MST-F2 pose extrema | FAIL parcial: sem NaN, ombreira solta |
| MST-F3 alongamento | FAIL: p99 1,51× (meta 1,5×) |
| MST-F4 peças removíveis | PASS: 25 objetos |

Transplante de punhos e colar (t07): FAIL, revertido.

### Decisão humana e textura (2026-11-07)

| Item | Resultado |
|---|---|
| G3M | APPROVED pelo usuário, somente como forma base (t09) |
| G9 | Permanece REJECTED |
| Textura (`paint/t03`) | REVIEW: cabeça com identidade, corpo chapado; verso estimado |

## Chibi, 2026-11-07

`ics run` em `aprendiz_chibi.json` e `aprendiz_floresta.json`: G1, G7 e G8 PASS; G3, G4, G5 e G9 REVIEW; G6 WARN (IMG-005, 2 frames repetidos no idle). GODOT-001 e GODOT-002 PASS. `pytest`: 47 passam. G6 barrou duas vezes o enquadramento, corrigido por escala e pivô. Hem esticado e joelho atravessando a túnica foram vistos na folha de sprites, não pelos gates. Nenhuma aprovação artística foi registrada; G9 `REJECTED` continua no histórico.

## Auditoria do mestre e detalhamento, 2026-11-07

- `ics run` em `aprendiz_chibi`, 5 variações, `aprendiz_pixel_128/192`, `aprendiz_detalhado_128/192/256` e `aprendiz_detalhado_suave`: G1, G7 e G8 PASS em todos; G6 WARN (IMG-005, 3 frames repetidos no idle); G3, G4, G5 e G9 REVIEW.
- Sonda de pose (`scripts/master_audit_pose.py`): nada abaixo do chão depois das correções; coxa fora da túnica ≤ 11,4 mm em 2 quadros da corrida, atrás.
- Transparência (`scripts/master_audit_alpha.py`): pixel art 216/216; o suave mestre tem 2.060 px de franja clara e 12 px semitransparentes no miolo.
- Prova modular (`scripts/master_audit_modular.py`): cada variação muda só as peças do componente trocado.
- `pytest`: 52 passam (5 novos do compositor de pixel art).
- Nenhuma aprovação artística registrada; G9 `REJECTED` antigo segue no histórico.

