# 16 — Princípios de confiabilidade e limites da IA

## 1. Objetivo

Definir o que o software pode garantir, o que pode medir, o que pode apenas estimar e o que exige inspeção humana. A arquitetura não deve prometer eliminar todos os erros de IA.

## 2. Princípio de fonte de verdade

A imagem gerada por IA é uma **referência visual**, não a fonte técnica definitiva do personagem.

A fonte de verdade de produção deve ser formada por:

- `CharacterSpec`: identidade e parâmetros do personagem;
- `BuildManifest`: componentes e versões usados;
- malha 3D e materiais aprovados;
- rig semântico e seu mapa de ossos;
- ações de animação e eventos de contato;
- `RenderProfile`: câmera, iluminação, escala e coordenadas;
- manifesto de exportação e evidências de QA.

A renderização 2D é derivada desses elementos. Não gerar cada direção ou cada frame por uma chamada de IA independente.

## 3. Limites explícitos

O sistema NÃO pode garantir automaticamente:

- que qualquer imagem de referência possua anatomia correta;
- que uma IA converta qualquer desenho em malha 3D utilizável sem retopologia, limpeza e rigging;
- que um detector visual entenda sempre qual membro pertence ao lado anatômico esquerdo/direito;
- que uma métrica matemática determine se um personagem é bonito, culturalmente respeitoso ou fiel à intenção do artista;
- que todo movimento seja biomecanicamente correto em qualquer espécie;
- que semelhança de cor ou de embedding prove identidade visual;
- que aprovação técnica substitua aprovação artística.

No MVP, a IA gera/auxilia referências e especificações. O personagem é construído a partir de uma biblioteca 3D controlada e validada. Geração livre de malha por IA fica fora do MVP.

## 4. Camadas de confiança

| Camada | O que garante | Como prova |
|---|---|---|
| Contrato | Campos, enums e compatibilidade de dados | JSON Schema/Pydantic e testes |
| Estrutura 3D | Objetos, malhas, rig e hierarquia presentes | Inspeção via Blender Python |
| Semântica | Ossos identificados como lado esquerdo/direito e função | Nomes, metadata, mapa de rig e poses sentinela |
| Animação | Quadros avaliados e contatos definidos | Curvas, pontos de apoio, eventos e testes por frame |
| Render | Câmera, fundo, tamanho e pivot conformes | Parâmetros de cena e análise de imagem |
| Temporal | Movimento sem saltos ou desalinhamentos indevidos | Métricas entre frames e revisão de loop |
| Artística | Correspondência ao conceito e direção de arte | Revisão humana com referências aprovadas |
| Runtime | O jogo carrega e reproduz o asset | Projeto de integração executado no Godot |

## 5. Papel da IA

A IA pode:

- interpretar descrições;
- propor variações de design;
- gerar concept art;
- sugerir peças existentes no catálogo;
- classificar possíveis defeitos em imagens;
- explicar alertas de QA.

A IA não pode:

- renomear ou inferir sozinha os ossos definitivos sem validação;
- alterar a orientação canônica silenciosamente;
- aprovar exportação quando testes obrigatórios falharam;
- substituir um rig validado por uma imagem;
- marcar como aprovado algo que não foi executado.

## 6. Níveis de aprovação

- **PASS:** requisito verificável passou automaticamente.
- **WARN:** existe uma suspeita ou condição dentro de tolerância, precisa ser exibida.
- **FAIL:** violação objetiva, bloqueia a etapa seguinte.
- **REVIEW:** exige decisão visual ou semântica humana.
- **NOT_TESTED:** teste não executado; nunca converter em PASS.

## 7. Regra de bloqueio

A exportação de produção só é liberada quando todos os testes obrigatórios automáticos passam e todas as revisões humanas requeridas foram aprovadas. Exportação experimental pode existir, mas deve carregar claramente o estado `UNAPPROVED` no manifesto.

## 8. Por que 3D ajuda, mas não resolve tudo

Um modelo 3D e um rig semântico removem classes inteiras de inconsistências de imagens independentes: a geometria é compartilhada entre câmeras, os membros estão conectados a ossos identificados e o z-buffer resolve a oclusão da cena. Ainda assim, uma malha pode ser ruim, pesos podem deformar, um rig pode estar espelhado e uma animação pode escorregar. Por isso a validação precisa cobrir estrutura, semântica, pose, tempo, imagem e integração.
