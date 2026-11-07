# 22 — Plano autônomo de execução para Claude Code

## 1. Objetivo

Transformar toda a documentação em uma sequência de tarefas executáveis. Este documento complementa `CLAUDE_CODE_START_HERE.md` e o guia de implementação.

## 2. Fase A — Descoberta e proteção do repositório

Antes de codificar:

- identificar raiz do repositório;
- detectar se já existe código, assets, testes ou documentação;
- executar `git status` e registrar alterações existentes;
- identificar o sistema operacional;
- detectar versões de Python, Blender, Godot, Node e Tauri;
- localizar ferramentas instaladas sem presumir caminhos;
- identificar limitações do hardware;
- nunca apagar ou substituir trabalho existente.

Saída: `docs/ENVIRONMENT_REPORT.md` e inventário inicial.

## 3. Fase B — Especificação executável

- consolidar `CharacterSpec`, `RigProfile`, `AnimationProfile`, `RenderProfile`, `BuildManifest` e `ExportManifest`;
- definir schemas versionados;
- definir `DirectionConvention` e conversão de coordenadas;
- criar dados de teste e fixtures;
- criar testes unitários para validação dos contratos;
- documentar campos obrigatórios e migração de schema.

Não iniciar interface completa antes dessa fase passar.

## 4. Fase C — Blender headless mínimo

- localizar executável Blender por configuração;
- executar `--version` e validar retorno;
- executar um script mínimo em background;
- criar cena, câmera ortográfica, luz e objeto de teste;
- ativar transparência quando suportada no motor/versão selecionados;
- renderizar PNG RGBA;
- validar assinatura, dimensões, alpha e arquivo;
- guardar log de stdout/stderr e código de saída;
- aplicar timeout e encerramento de processo;
- testar caminho com espaços e caracteres não ASCII no Windows.

Não presumir que um caminho fixo do computador do usuário exista.

## 5. Fase D — Rig de referência e teste semântico

- construir um humanoide-base simplificado ou importar asset licenciado;
- criar mapa de ossos semânticos;
- inserir marcadores de QA;
- validar hierarquia;
- executar poses sentinela para cada membro;
- renderizar debug views;
- confirmar que a perna/mão esquerda semântica é a que se move;
- confirmar a projeção em todas as oito direções;
- produzir evidências antes de usar rig em personagem final.

## 6. Fase E — Animações

- criar idle e walk no rig-base;
- definir eventos de contato;
- validar foot sliding e ground contact;
- renderizar todos os frames das oito direções;
- gerar previews e relatórios;
- corrigir antes de expandir o conjunto de animações.

## 7. Fase F — Godot vertical slice

- criar projeto de teste na versão validada;
- importar PNGs;
- criar SpriteFrames/AnimatedSprite2D ou o mecanismo escolhido com justificativa;
- reproduzir animações e trocar direção;
- automatizar o smoke test se possível;
- comprovar visualmente o resultado em execução.

A integração só passa quando o projeto abre e reproduz corretamente, não apenas quando os arquivos aparecem na pasta.

## 8. Fase G — UI e assistente IA

Somente após o vertical slice:

- criar app desktop Tauri/React;
- implementar gerenciamento de projetos;
- designer e visualizador;
- integração com IA por provider;
- workflow de aprovação de conceito;
- biblioteca de componentes;
- jobs com retomada e cache;
- export center.

O provider IA deve ser opcional para não bloquear a geração com componentes existentes.

## 9. Fase H — Expansão e produção

- variações de humanoides;
- famílias quadrúpedes com rig próprio;
- criaturas especiais;
- geração em lote;
- perfis de qualidade e desempenho;
- empacotamento Windows;
- testes de instalação e atualização.

## 10. Política de bloqueios

Se uma ferramenta não estiver instalada, pesquisar o procedimento oficial, verificar compatibilidade e tentar configuração local não destrutiva. Se houver barreira de licença, pagamento, credencial ou hardware sem alternativa segura/gratuita, documentar o bloqueio e continuar tarefas independentes.

Não trocar tecnologia silenciosamente para “fazer passar”. Propor substituição tecnicamente equivalente, registrar impactos e continuar quando for reversível.

## 11. Execução incremental contínua

Ao concluir um incremento:

1. executar os testes;
2. atualizar STATUS, DECISIONS, VALIDATION_REPORT;
3. registrar commit ou estado Git, se o repositório usar Git;
4. escolher a próxima tarefa desbloqueada;
5. continuar sem solicitar aprovação para ações rotineiras;
6. parar somente diante de bloqueio real ou limite operacional.

## 12. Resultado final esperado

O agente deve produzir uma aplicação que realmente execute o pipeline. A documentação e a interface não contam como implementação do motor. O sucesso é medido por assets reproduzíveis, testes e integração verificada.
