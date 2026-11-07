# 14 — Guia de implementação para Codex

> **Atualização importante:** este guia foi complementado por `CLAUDE_CODE_START_HERE.md`, `16_PRINCIPIOS_DE_CONFIABILIDADE_E_LIMITES_DA_IA.md`, `17_VALIDACAO_DE_RIG_ANATOMIA_E_ORIENTACAO.md`, `18_VALIDACAO_DE_ANIMACAO_E_CONTINUIDADE.md`, `19_TESTES_VISUAIS_GOLDEN_IMAGES_E_QA.md`, `20_QUALITY_GATES_E_APROVACAO.md`, `21_PESQUISA_TECNICA_E_REFERENCIAS.md`, `22_PLANO_AUTONOMO_DE_EXECUCAO_CLAUDE_CODE.md` e `23_MATRIZ_DE_TESTES_E_EVIDENCIAS.md`. Para execução autônoma, siga primeiro `CLAUDE_CODE_START_HERE.md`.

## 1. Papel do agente de desenvolvimento

Implementar o Isometric Character Studio conforme esta documentação, sem alterar decisões arquiteturais silenciosamente. O agente deverá trabalhar em incrementos pequenos, executáveis e verificáveis.

## 2. Fontes de verdade

Prioridade das referências:

1. decisões explicitamente aprovadas pelo usuário;
2. `00_SUMARIO_E_DECISOES.md`;
3. `04_ARQUITETURA_TECNICA.md`;
4. contratos em `06_CONTRATOS_DE_DADOS.md`;
5. critérios de aceite em `12_MVP_E_CRITERIOS_DE_ACEITE.md`;
6. demais documentos deste pacote.

Quando houver contradição, não escolher silenciosamente. Registrar a divergência e propor resolução.

## 3. Regras obrigatórias

- Não implementar todos os módulos em um único passo.
- Não criar interfaces visuais completas antes de validar o vertical slice técnico.
- Não acoplar domínio à UI, Blender ou Godot.
- Não simular funcionalidades que ainda não existem.
- Não declarar integração concluída sem executar o projeto Godot de teste.
- Não afirmar que IA gera qualquer modelo 3D se o mecanismo real for seleção/montagem de componentes.
- Não substituir geração 3D por imagens independentes de IA para as oito direções.
- Não adicionar Redis, Kubernetes, microserviços ou infraestrutura distribuída sem necessidade demonstrada.
- Não instalar dependências sem justificar e registrar a finalidade.
- Não inserir assets sem registrar origem e licença.
- Não modificar contratos sem atualizar schemas, testes e documentação.

## 4. Forma de trabalho

Para cada tarefa:

1. inspecionar o repositório e o estado atual;
2. identificar documentos e módulos afetados;
3. propor um plano curto, com arquivos previstos;
4. implementar apenas o escopo solicitado;
5. executar testes e validações relevantes;
6. registrar comandos executados e resultados reais;
7. atualizar documentação;
8. listar limitações, riscos e próximos passos.

Não perguntar novamente informações já registradas nos documentos.

## 5. Política de mudanças arquiteturais

Uma alteração de stack, contrato, convenção de direção ou responsabilidade de módulo deve vir acompanhada de:
- motivo técnico;
- opções consideradas;
- impacto em módulos existentes;
- migração necessária;
- testes afetados;
- atualização documental.

## 6. Escopo e precedência para agentes atuais

Este guia foi escrito originalmente como orientação de implementação incremental para Codex e contém um prompt de início limitado à fundação técnica. Para a execução autônoma atual com Claude Code, a ordem de leitura e o plano completo em `CLAUDE_CODE_START_HERE.md` e `22_PLANO_AUTONOMO_DE_EXECUCAO_CLAUDE_CODE.md` têm precedência.

O princípio deste guia continua válido: não implementar o produto inteiro em um salto; entregar e provar cada fase. O primeiro incremento continua sendo a fundação/vertical slice, mas o agente deverá prosseguir para as fases seguintes quando os critérios da fase anterior passarem, sem exigir uma nova explicação do usuário.

Entregas esperadas:
- repositório organizado;
- backend mínimo;
- contrato `CharacterSpec` inicial;
- chamada controlada ao Blender em background;
- cena de teste automatizada;
- render PNG com transparência;
- verificação de saída;
- projeto Godot mínimo que importa o PNG;
- documentação de execução no Windows.

Não implementar ainda a geração automática de concept art, a biblioteca completa, a UI completa ou geração de personagens arbitrários.

## 7. Critério para declarar uma tarefa concluída

Uma tarefa só está concluída quando:
- código está no local correto;
- comportamento foi executado;
- testes relevantes passaram;
- falhas conhecidas foram registradas;
- documentação acompanha o estado real;
- nenhum resultado foi inventado ou presumido.

## 8. Prompt legado de início para Codex

> Este prompt é limitado à Fase 0. Para Claude Code e execução contínua, use `CLAUDE_CODE_START_HERE.md`.

```text
Leia integralmente a documentação do Isometric Character Studio, começando pelo README.md e pelos documentos 00, 04, 06, 11, 12 e 14.

Inspecione o repositório atual antes de alterar arquivos. Não implemente o produto inteiro. Execute somente a Fase 0 — Fundação técnica.

Seu objetivo é provar, em ambiente Windows, a comunicação entre um backend Python local, um processo Blender executado em background e um projeto mínimo Godot 4. O fluxo deverá produzir um PNG RGBA automatizado, validar sua existência/dimensões/transparência e demonstrar sua importação no Godot.

Respeite os contratos, mantenha os módulos desacoplados, registre versões e comandos executados, crie testes e atualize a documentação. Não simule resultados nem declare uma validação que não tenha sido executada. Ao final, apresente arquivos alterados, testes executados, evidências, limitações e o próximo passo recomendado.
```
