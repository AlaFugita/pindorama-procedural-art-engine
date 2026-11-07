# 05 — Especificação dos módulos

## 1. Project Manager

**Responsabilidade:** criar, abrir, salvar, versionar e organizar projetos.

Entradas:
- nome do projeto;
- perfil artístico;
- diretório de trabalho;
- configurações gerais.

Saídas:
- registro persistido;
- estrutura inicial de diretórios;
- identificador estável do projeto.

Não deve executar geração de imagem ou Blender diretamente.

## 2. Character Designer

**Responsabilidade:** oferecer a experiência de criação e edição de personagens.

Funções:
- formulário de atributos;
- edição de texto;
- escolha de família;
- seleção de componentes;
- edição de paleta;
- visualização de especificação;
- aprovação de conceito.

A UI chama serviços do backend e não modifica arquivos de produção por conta própria.

## 3. AI Engine

**Responsabilidade:** assistência generativa.

Subcomponentes:
- `PromptInterpreter`: converte linguagem natural em proposta estruturada;
- `ConceptProvider`: gera referências visuais;
- `ComponentRecommender`: sugere itens existentes na biblioteca;
- `ConsistencyReviewer`: aponta possíveis diferenças entre referência e resultado.

A IA deve devolver resultados que possam ser validados. Respostas não estruturadas devem ser tratadas como rascunhos, nunca como configuração aprovada.

## 4. Asset Library

**Responsabilidade:** catalogar e fornecer componentes.

Tipos:
- corpos e cabeças;
- cabelo;
- roupas;
- armaduras;
- acessórios;
- armas;
- materiais;
- rigs;
- animações;
- perfis de câmera e renderização.

Cada asset precisa de ID, versão, licença, família compatível, escala, ancoragens e dependências.

## 5. Character Builder

**Responsabilidade:** montar a cena 3D a partir do `CharacterSpec` e do `BuildManifest`.

Operações:
- carregar template da família;
- instanciar componentes;
- alinhar pontos de ancoragem;
- aplicar materiais;
- validar dependências;
- salvar projeto de origem.

Não deverá tentar gerar topologia arbitrária no MVP.

## 6. Rig Engine

**Responsabilidade:** associar personagem a um esqueleto e validar compatibilidade.

Operações:
- identificar perfil de rig;
- verificar hierarquia e nomes de ossos esperados;
- verificar pesos e deformações básicas;
- aplicar/confirmar rig;
- registrar versão.

## 7. Animation Engine

**Responsabilidade:** selecionar e executar animações compatíveis.

Operações:
- listar animações por família;
- associar clip;
- configurar FPS, loop e duração;
- reproduzir preview;
- validar início/fim e transições.

## 8. Render Engine

**Responsabilidade:** produzir frames consistentes.

Operações:
- aplicar `RenderProfile`;
- configurar resolução e transparência;
- posicionar câmera nas oito direções;
- renderizar sequência de animação;
- registrar parâmetros e resultados.

## 9. Post-processing Engine

**Responsabilidade:** tratar imagens já renderizadas.

Operações:
- validar dimensões;
- preservar canal alpha;
- recortar ou manter canvas fixo conforme perfil;
- alinhar ponto de apoio;
- gerar atlas/spritesheet;
- produzir mapa de frames e metadados.

Evitar redimensionamento independente de cada direção, pois isso pode causar variação de escala.

## 10. Validator

**Responsabilidade:** decidir se uma saída pode ser exportada.

Categorias:
- integridade de arquivos;
- dimensões e alpha;
- quantidade de direções/frames;
- alinhamento;
- metadados;
- compatibilidade de destino;
- avisos visuais que exigem revisão humana.

A validação visual automatizada não substitui aprovação artística.

## 11. Export Engine

**Responsabilidade:** criar o pacote final.

Operações:
- copiar arquivos para estrutura de destino;
- gerar `manifest.json`;
- gerar metadados do jogo;
- incluir fontes opcionais;
- registrar hashes e versões;
- emitir relatório de exportação.

## 12. Godot Export Bridge

**Responsabilidade:** facilitar a utilização no Godot.

Pode gerar:
- estrutura de diretórios;
- cenas de demonstração;
- recursos `SpriteFrames`, quando apropriado;
- scripts auxiliares de seleção de direção;
- arquivo de configuração de importação, se necessário e validado.

O Bridge não será responsável por lógica de movimentação ou gameplay do MMORPG.
