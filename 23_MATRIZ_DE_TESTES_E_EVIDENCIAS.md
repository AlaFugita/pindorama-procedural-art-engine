# 23 — Matriz de testes e evidências

## 1. Objetivo

Fornecer uma lista única de testes para implementação e auditoria. Cada linha precisa apontar para um teste executável ou evidência manual registrada.

## 2. Matriz inicial

| ID | Área | Teste | Tipo | Bloqueia produção |
|---|---|---|---|---|
| ENV-001 | Ambiente | Versões detectadas e compatíveis | Automático | Sim |
| SPEC-001 | Contrato | CharacterSpec válido | Unitário | Sim |
| SPEC-002 | Contrato | IDs duplicados e campos desconhecidos tratados | Unitário | Sim |
| BL-001 | Blender | Processo background inicia e termina | Integração | Sim |
| BL-002 | Blender | Caminho com espaços funciona | Integração | Sim |
| RND-001 | Render | PNG RGBA válido | Integração | Sim |
| RND-002 | Render | Câmera ortográfica e escala corretas | Automático + revisão | Sim |
| RIG-001 | Rig | Hierarquia obrigatória existe | Automático | Sim |
| RIG-002 | Rig | Poses sentinela movem o membro esperado | Automático + revisão | Sim |
| RIG-003 | Rig | Esquerda/direita não trocadas nas oito direções | Automático | Sim |
| RIG-004 | Rig | Pesos e deformações passam | Automático + revisão | Sim |
| ANI-001 | Animação | Todos os frames avaliados | Automático | Sim |
| ANI-002 | Animação | Eventos de contato coerentes | Automático + revisão | Sim |
| ANI-003 | Animação | Foot sliding dentro do perfil | Automático + revisão | Sim |
| ANI-004 | Animação | Loop sem salto indevido | Automático + revisão | Sim |
| DIR-001 | Direções | Oito IDs e headings mapeados | Automático | Sim |
| IMG-001 | Imagem | Alpha/transparência correta | Automático | Sim |
| IMG-002 | Imagem | Sem corte e pivot consistente | Automático + revisão | Sim |
| IMG-003 | Imagem | Atlas e retângulos válidos | Automático | Sim |
| EXP-001 | Export | Manifesto lista todos os arquivos | Automático | Sim |
| EXP-002 | Export | Hashes e metadados coerentes | Automático | Sim |
| GODOT-001 | Runtime | Projeto importa os PNGs | Integração | Sim |
| GODOT-002 | Runtime | Reproduz animação e direção corretas | E2E + revisão | Sim |
| ART-001 | Arte | Concept versus modelo aprovado | Humano | Sim |
| ART-002 | Arte | Silhueta/legibilidade em escala de jogo | Humano | Sim |

## 3. Estrutura de evidências

```text
artifacts/
└── validation/
    └── <run_id>/
        ├── environment.json
        ├── test_results.xml
        ├── logs/
        ├── renders/
        ├── contact_sheets/
        ├── animation_previews/
        ├── image_diffs/
        ├── godot_smoke_test/
        └── report.md
```

Não versionar outputs gigantes indiscriminadamente. Registrar política de retenção; manter fixtures/golden assets pequenos e necessários no repositório.

## 4. Formato de resultado

Cada teste deve registrar:

- ID do teste;
- data/hora;
- versão do código;
- máquina/ambiente relevante;
- comando;
- resultado `PASS`, `FAIL`, `WARN`, `REVIEW` ou `NOT_TESTED`;
- saída observada;
- tolerância aplicada;
- artefato de evidência;
- observação de limitação.

## 5. Relatório geral

`docs/VALIDATION_REPORT.md` deve conter contagem por status, testes bloqueadores, link para evidências e decisão sobre liberação. Qualquer `NOT_TESTED` em teste bloqueador impede o estado production.
