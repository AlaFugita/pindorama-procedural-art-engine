# 12 — MVP e critérios de aceite

## 1. Objetivo do MVP

Provar que o produto consegue criar um personagem humanoide a partir de componentes 3D controlados, animá-lo, renderizá-lo em oito direções e exportá-lo para Godot.

## 2. Personagem de validação

Primeiro caso: **Guardião da Floresta**, um humanoide estilizado. A inspiração visual pode incluir referências brasileiras e indígenas específicas, desde que pesquisadas e documentadas. O objetivo técnico é validar cabelo, roupa, ornamentos, arma e silhueta com alguns componentes assimétricos.

## 3. Escopo obrigatório

- uma família humanoide;
- pelo menos uma base corporal;
- cabeça e cabelo substituíveis;
- algumas peças de vestuário;
- acessórios e arma;
- perfil artístico versionado;
- rig humanoide;
- clips idle, walk e run;
- oito direções;
- PNG RGBA;
- metadados JSON;
- validação automática;
- cena de demonstração Godot.

## 4. Critérios de aceite

### CA-001 — Criação de especificação

Dado um `CharacterSpec` válido, o sistema cria um projeto e identifica assets ausentes ou incompatíveis antes de montar a cena.

### CA-002 — Montagem

A montagem gera uma cena Blender e um `BuildManifest` com componentes e versões utilizados.

### CA-003 — Variações

Três variações de aparência podem ser produzidas sem duplicar todo o pipeline de construção.

### CA-004 — Rig

O personagem é associado ao rig humanoide esperado e passa nas validações estruturais definidas.

### CA-005 — Animações

Idle, walk e run podem ser executadas e revisadas no Blender.

### CA-006 — Oito direções

Cada animação selecionada gera oito conjuntos de frames seguindo a ordem canônica N, NE, E, SE, S, SW, W, NW.

### CA-007 — Consistência espacial

O personagem mantém escala, canvas e pivô estáveis entre quadros e direções, dentro da tolerância definida nos testes.

### CA-008 — Integridade de imagem

Arquivos PNG têm dimensões previstas, canal alpha e ausência de recortes indevidos.

### CA-009 — Metadados

O manifest descreve corretamente animações, direções, FPS, frames, pivôs e caminhos.

### CA-010 — Importação Godot

O projeto de teste importa os arquivos e reproduz idle, walk e run nas oito direções.

### CA-011 — Recuperação

Falha simulada em uma etapa não apaga outputs válidos de etapas anteriores nem exportações aprovadas.

### CA-012 — Reprodutibilidade

Um job registra inputs, versões, parâmetros, logs e arquivos produzidos.

## 5. Evidências obrigatórias

- arquivo `.blend` do personagem;
- render de referência;
- contact sheet com oito direções;
- spritesheets de idle, walk e run;
- `CharacterSpec`;
- `BuildManifest`;
- `ExportManifest`;
- relatório de validação;
- projeto Godot de teste;
- vídeo ou captura mostrando animações e troca de direção.

## 6. O que não comprova o MVP

- uma única imagem gerada por IA;
- um concept sheet sem modelo 3D reutilizável;
- oito imagens feitas manualmente sem pipeline reproduzível;
- spritesheets sem metadados;
- arquivos que não foram importados e testados no Godot.
