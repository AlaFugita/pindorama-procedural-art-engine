# 00 — Sumário executivo e decisões

## 1. Resumo executivo

O **Isometric Character Studio** será uma aplicação desktop independente para produção de personagens estilizados destinados a um MMORPG 2.5D isométrico. O produto combinará:

- IA para transformar descrições em especificações estruturadas, gerar concept art e sugerir componentes;
- biblioteca de modelos 3D, peças modulares, materiais e rigs;
- automação do Blender para montagem, animação e renderização;
- geração de oito direções por animação;
- pós-processamento e empacotamento de frames;
- exportação com metadados e integração inicial com Godot 4.

O objetivo não é apenas produzir uma imagem bonita. O resultado precisa ser consistente, editável, reproduzível e integrável ao jogo.

## 2. Decisões consolidadas

| ID | Decisão | Estado |
|---|---|---|
| DEC-001 | Aplicativo desktop independente | Confirmada |
| DEC-002 | Estratégia híbrida IA + 3D modular | Confirmada |
| DEC-003 | Oito direções | Confirmada |
| DEC-004 | Humanoides como primeira família | Proposta de execução aprovada |
| DEC-005 | Godot 4 como primeira integração | Confirmada |
| DEC-006 | Blender como motor de construção e renderização | Recomendação técnica |
| DEC-007 | Tauri + React + TypeScript na interface | Recomendação técnica |
| DEC-008 | Python + FastAPI no backend local | Recomendação técnica |
| DEC-009 | SQLite para metadados locais no MVP | Recomendação técnica |
| DEC-010 | PNG + JSON como pacote 2D de saída | Confirmada como formato principal |
| DEC-011 | `.blend` como fonte editável e GLB como formato de intercâmbio opcional | Recomendação técnica |

## 3. Princípio de consistência

O sistema não deve produzir cada direção como uma imagem independente. Deve manter uma fonte de verdade 3D e renderizar vistas dela.

Isso permite manter:

- identidade facial;
- proporções corporais;
- roupas e acessórios;
- materiais e cores;
- escala e ponto de apoio;
- iluminação e câmera;
- continuidade entre quadros de uma animação.

## 4. Limite realista da automação por IA

A expressão “gerar qualquer personagem” representa a ambição do produto, não uma capacidade que o MVP já terá.

No MVP, a criação 3D será baseada em uma família humanoide e em componentes previamente preparados. A IA interpretará o pedido, proporá conceitos e ajudará a selecionar/configurar componentes. A geração arbitrária de malhas 3D de qualquer criatura não é requisito do MVP e deverá ser tratada como pesquisa e desenvolvimento posterior.

## 5. Primeiro resultado verificável

Um personagem humanoide estilizado deverá percorrer todo o pipeline:

1. receber um `CharacterSpec`;
2. montar um modelo 3D a partir de componentes;
3. aplicar rig compatível;
4. executar idle, walk e run;
5. renderizar oito direções;
6. produzir PNGs e metadados;
7. passar pela validação automática;
8. ser importado e animado em uma cena de teste do Godot.

## 6. Critério de sucesso do produto

O sucesso não será medido apenas pela capacidade de gerar concept art. Será medido pela capacidade de criar e exportar personagens consistentes, com esforço repetível e qualidade aceitável para produção do MMORPG.
