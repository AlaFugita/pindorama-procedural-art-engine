# 01 — Visão do produto e escopo

## 1. Visão

Criar uma ferramenta de produção visual que permita a artistas e desenvolvedores gerar, personalizar, animar, revisar e exportar personagens para um MMORPG 2.5D isométrico, mantendo uma direção artística consistente.

## 2. Problema que o produto resolve

A produção manual de muitos personagens exige repetir tarefas de modelagem, montagem, rigging, animação, renderização e organização dos arquivos. A geração direta de imagens por IA, por sua vez, pode produzir inconsistências entre ângulos e quadros.

O software deverá combinar a velocidade criativa da IA com a previsibilidade de uma fonte 3D reutilizável.

## 3. Usuários principais

- Desenvolvedor independente de jogos;
- artista técnico ou artista 3D;
- designer de personagens;
- equipe pequena de produção de MMORPG;
- equipe que utiliza Godot como motor de jogo.

## 4. Casos de uso

### UC-001 — Criar personagem por descrição

O usuário descreve um personagem. O sistema gera uma especificação estruturada e referências visuais. O usuário revisa e aprova antes da construção 3D.

### UC-002 — Criar personagem pela biblioteca

O usuário seleciona uma base corporal, cabeça, cabelo, roupas, acessórios, materiais e cores.

### UC-003 — Modificar um personagem existente

O usuário altera um componente e gera novamente apenas os resultados afetados, quando tecnicamente possível.

### UC-004 — Aplicar animações

O usuário escolhe movimentos compatíveis com a família de rig do personagem e visualiza o resultado.

### UC-005 — Renderizar oito direções

O usuário seleciona animações e perfis de renderização. O sistema produz as oito direções sem espelhamento artificial.

### UC-006 — Exportar para Godot

O usuário exporta texturas, frames, atlas, metadados e, quando aplicável, um pacote 3D de origem/intercâmbio.

### UC-007 — Reabrir e versionar

O usuário abre um projeto anterior, modifica-o e mantém versões e manifests para rastrear a origem dos assets.

## 5. Escopo do MVP

Incluído:

- aplicativo desktop funcional em Windows;
- backend local;
- um perfil artístico inicial;
- uma família de rig humanoide;
- biblioteca pequena de componentes 3D;
- montagem de personagem via especificação;
- animações idle, walk e run;
- renderização ortográfica em oito direções;
- PNGs e metadados;
- validação básica;
- exportação para uma cena de teste Godot.

## 6. Fora do escopo do MVP

- criação automática de qualquer malha 3D a partir de texto;
- suporte completo a todas as espécies e anatomias;
- marketplace ou distribuição pública de assets;
- colaboração multiusuário em tempo real;
- render farm distribuída;
- editor 3D completo que substitua o Blender;
- sistema de gameplay ou movimentação do MMORPG;
- geração de mapas, cenários ou efeitos visuais do jogo;
- garantia de que todos os assets produzidos por IA estejam livres de restrições de licença.

## 7. Evolução desejada

Após validar a família humanoide, o sistema poderá receber famílias de quadrúpedes, criaturas grandes, seres voadores e monstros especiais. Cada família terá componentes, rigs, animações e regras de renderização próprias.

## 8. Princípios do produto

1. Consistência acima de geração aleatória.
2. Reprodutibilidade acima de resultados não rastreáveis.
3. Componentes reutilizáveis acima de soluções específicas por personagem.
4. IA como assistência, sem substituir validação.
5. Exportação previsível e documentada.
6. Independência do motor de jogo, mantendo Godot como primeiro destino.

## 9. Adendo de 2026-11-07: visão de longo prazo, Procedural Art Engine

O Isometric Character Studio continua sendo o produto. Ele passa a ter como **visão de longo prazo** virar uma plataforma de geração procedural de arte para videogames: assets feitos por código, geometria, matemática, materiais e renderização, sem depender de imagem pré-desenhada, desenho manual, IA generativa ou biblioteca pronta.

- **Primeiro domínio, e único no MVP:** personagens. As criaturas vêm em seguida.
- **Domínios futuros, ainda fora do MVP:** natureza, objetos, materiais, construções e ambientes. A exclusão do §6 vale para o MVP, não para a visão.
- **IA:** passa a ser ferramenta **opcional** de assistência e análise. O núcleo de geração precisa funcionar sem ela, e hoje já funciona. Isso substitui a ênfase do §2 em "velocidade criativa da IA".
- **Concluído:** um asset só está concluído quando é **utilizável no jogo**, com estrutura, animação, transparência, pivô, exportação e compatibilidade com a engine.

Mapeamento do estado real: [docs/audit/MATRIZ_ADERENCIA_PROCEDURAL_ART_ENGINE_2026-11-07.md](docs/audit/MATRIZ_ADERENCIA_PROCEDURAL_ART_ENGINE_2026-11-07.md).
