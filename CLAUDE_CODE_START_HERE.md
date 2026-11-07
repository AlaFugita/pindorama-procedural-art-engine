# LEIA PRIMEIRO — Instruções de execução para Claude Code

> Este arquivo é a porta de entrada operacional do projeto. Foi escrito para que um agente de desenvolvimento consiga começar sem depender de uma explicação oral adicional.

## Missão

Você é o agente técnico responsável por transformar esta documentação em um software funcional chamado **Isometric Character Studio**: um aplicativo desktop independente para criação assistida por IA, montagem 3D modular, rigging, animação, renderização isométrica em oito direções e exportação de personagens 2D para MMORPGs 2.5D, com integração inicial com Godot.

**Não interprete esta missão como autorização para afirmar que o produto já funciona.** Você deve inspecionar, pesquisar, implementar, executar, testar, corrigir e registrar evidências reais.

## Ordem obrigatória de leitura

1. Leia este arquivo inteiro.
2. Leia `README.md`.
3. Leia todos os documentos numerados de `00_...` até `23_...`, sem pular arquivos.
4. Leia `14_GUIA_DE_IMPLEMENTACAO_CODEX.md` e `22_PLANO_AUTONOMO_DE_EXECUCAO_CLAUDE_CODE.md` por inteiro.
5. Leia `21_PESQUISA_TECNICA_E_REFERENCIAS.md` e abra as fontes oficiais relevantes antes de implementar integrações.
6. Inspecione o repositório e o ambiente local antes de criar ou modificar qualquer arquivo.

Se algum arquivo listado não existir, registre o fato; não invente seu conteúdo.

## Objetivo inicial e ordem de execução

A implementação deve avançar por entregas verificáveis, começando pelo **vertical slice mínimo**:

1. ambiente e inventário de dependências;
2. contratos de dados versionados;
3. backend mínimo;
4. processo Blender executado de forma controlada em background;
5. cena 3D de teste determinística;
6. rig humanoide de referência com marcadores semânticos esquerdo/direito;
7. render de uma imagem RGBA com câmera ortográfica/isométrica;
8. teste automático de dimensões, alpha, enquadramento e integridade;
9. oito direções de referência com mapeamento inequívoco;
10. primeiro ciclo de animação controlado;
11. projeto Godot mínimo que carrega e reproduz os frames;
12. relatório de evidências.

Só depois de provar esse caminho, amplie para a interface completa, gerador de conceito por IA, catálogo modular e outras famílias de personagens. Não implemente todo o roadmap de uma vez.

## Regras de autonomia

- Não peça ao usuário para repetir decisões documentadas.
- Para decisões reversíveis e de baixo risco, escolha uma opção tecnicamente razoável, registre a justificativa e avance.
- Não interrompa o trabalho para pedir aprovação de cada arquivo ou pequena decisão.
- Peça intervenção humana somente quando houver bloqueio real: credencial privada, licença/uso de asset duvidoso, escolha artística que não pode ser inferida, alteração destrutiva, compra/serviço pago ou ausência de ferramenta essencial.
- Não faça compras, contrate serviços, publique conteúdo ou envie dados a terceiros sem autorização explícita.
- Não sobrescreva projetos existentes nem apague arquivos sem comprovar que são artefatos descartáveis gerados pelo próprio pipeline.
- Preserve qualquer trabalho preexistente no repositório.

## Pesquisa na internet é parte da tarefa

Quando a implementação depender de APIs, versões, formatos, bibliotecas, instalação ou compatibilidade:

1. pesquise primeiro a documentação oficial e a especificação primária;
2. confira a versão realmente instalada e a versão coberta pela documentação;
3. prefira referências oficiais, repositórios oficiais e especificações normativas;
4. consulte fontes secundárias somente quando a fonte primária não resolver a questão;
5. registre URLs, data de consulta, versão e decisão em `docs/research/RESEARCH_LOG.md` (crie esse arquivo se necessário);
6. não copie comandos de tutoriais antigos sem verificar se ainda existem;
7. nunca exponha chaves, tokens, caminhos pessoais ou dados privados em logs.

A lista inicial de fontes está em `21_PESQUISA_TECNICA_E_REFERENCIAS.md`. Ela é um ponto de partida, não uma lista fechada. Procure referências adicionais quando necessário.

## Política de verdade e evidências

- Diferencie **implementado**, **testado**, **validado visualmente**, **pendente** e **não suportado**.
- Um arquivo existir não significa que esteja correto.
- Um comando ter sido escrito não significa que tenha sido executado.
- Um teste não executado não pode ser reportado como aprovado.
- Um render bonito não comprova que o rig, a direção ou o ciclo de animação estejam corretos.
- Uma IA de visão pode apontar suspeitas, mas não certifica sozinha anatomia, semântica de membros ou intenção artística.
- Toda conclusão importante deve apontar para um teste, log, imagem, vídeo, arquivo ou inspeção reproduzível.

## Resultado esperado ao final de cada sessão

Atualize:

- `docs/STATUS.md`: estado real do produto;
- `docs/DECISIONS.md`: decisões técnicas e motivos;
- `docs/research/RESEARCH_LOG.md`: pesquisa consultada;
- `docs/VALIDATION_REPORT.md`: testes executados e resultados;
- documentação do módulo alterado.

Ao encerrar a sessão, informe de forma objetiva:

1. o que foi implementado;
2. os arquivos criados/modificados;
3. comandos realmente executados;
4. testes aprovados, reprovados e não executados;
5. evidências e caminhos dos artefatos;
6. limitações conhecidas;
7. próximo incremento exato.

## Definição de sucesso

O objetivo não é produzir uma grande quantidade de código. É construir uma cadeia pequena, correta, reproduzível e testada, expandindo-a progressivamente até chegar ao software descrito.
