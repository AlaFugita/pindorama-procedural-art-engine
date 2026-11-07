# Pindorama Procedural Art Engine (Isometric Character Studio)

Gerador procedural de personagens 2.5D isométricos para um MMORPG pessoal: geometria, rig, animação e render no Blender, composição em Python e exportação para o Godot.

- **Site do projeto (GitHub Pages):** https://alafugita.github.io/pindorama-procedural-art-engine/
- **Estado real:** [docs/STATUS.md](docs/STATUS.md) · **Decisões:** [docs/DECISIONS.md](docs/DECISIONS.md)
- **Começar:** `uv sync`, depois `uv run ics doctor` e `uv run ics run tests/fixtures/specs/aprendiz_suave_192.json` (precisa do Blender e do Godot em `tools/`; veja [docs/ENVIRONMENT_REPORT.md](docs/ENVIRONMENT_REPORT.md)).

---

# Isometric Character Studio — Documentação do Projeto

> Pacote de documentação técnica e de produto para um aplicativo independente de criação de personagens para MMORPGs 2.5D isométricos.

**Idioma:** português (Brasil)  
**Status:** arquitetura proposta — ainda não implementada  
**Versão da documentação:** 0.2.0  
**Plataforma inicial:** Windows  
**Destino inicial dos assets:** Godot 4

## Objetivo

Construir um software desktop que transforme uma descrição e/ou configuração visual em um personagem consistente, editável e reutilizável. A ferramenta combinará IA para assistência criativa com montagem 3D modular, rigging, animação, renderização ortográfica em oito direções e exportação de spritesheets e metadados.

O modelo 3D será a fonte de verdade visual. As imagens 2D serão renderizações derivadas desse modelo — não oito desenhos gerados independentemente por IA.

## Decisões de produto já tomadas

| Tema | Decisão |
|---|---|
| Formato | Aplicativo independente, com interface própria |
| Estratégia de criação | Híbrida: IA + construção 3D modular |
| Perspectiva de saída | 2.5D isométrica/ortográfica |
| Direções | 8 |
| Saída principal | PNGs, spritesheets/atlases e metadados |
| Fonte editável | Projeto 3D, preferencialmente `.blend`, com GLB quando aplicável |
| Integração inicial | Godot 4 |
| Primeira família | Humanoides estilizados |
| Primeiro caso de validação | Guardião da floresta, inspirado em referências visuais aprovadas |

## O que este pacote contém

| Documento | Conteúdo |
|---|---|
| [00 — Sumário e decisões](00_SUMARIO_E_DECISOES.md) | Resumo executivo, decisões e limites |
| [01 — Visão e escopo](01_VISAO_E_ESCOPO.md) | Objetivo, público, casos de uso e fora de escopo |
| [02 — Requisitos](02_REQUISITOS_FUNCIONAIS_NAO_FUNCIONAIS.md) | Requisitos e prioridades |
| [03 — Direção artística](03_DIRECAO_ARTISTICA.md) | Perfil visual, consistência e referências |
| [04 — Arquitetura técnica](04_ARQUITETURA_TECNICA.md) | Componentes, comunicação e decisões de tecnologia |
| [05 — Módulos](05_ESPECIFICACAO_MODULOS.md) | Responsabilidades e limites dos módulos |
| [06 — Contratos de dados](06_CONTRATOS_DE_DADOS.md) | `CharacterSpec`, jobs e manifests |
| [07 — Pipeline](07_PIPELINE_DE_GERACAO.md) | Fluxo de criação e estados de execução |
| [08 — Renderização e animação](08_RENDERIZACAO_E_ANIMACAO.md) | Direções, câmera, rigs e quadros |
| [09 — Exportação Godot](09_EXPORTACAO_E_INTEGRACAO_GODOT.md) | Formatos, convenções e integração |
| [10 — Estrutura do repositório](10_ESTRUTURA_DO_REPOSITORIO.md) | Organização inicial do código e conteúdo |
| [11 — Roadmap](11_ROADMAP_DE_IMPLEMENTACAO.md) | Fases e dependências |
| [12 — MVP e critérios de aceite](12_MVP_E_CRITERIOS_DE_ACEITE.md) | Escopo mínimo e testes de conclusão |
| [13 — Riscos e decisões abertas](13_RISCOS_E_DECISOES_ABERTAS.md) | Riscos, mitigação e pontos a validar |
| [14 — Guia para Codex](14_GUIA_DE_IMPLEMENTACAO_CODEX.md) | Regras para agentes de desenvolvimento |
| [15 — Glossário](15_GLOSSARIO.md) | Termos usados na documentação |

## Documentação complementar de confiabilidade e execução autônoma

| Documento | Conteúdo |
|---|---|
| [Início — Claude Code](CLAUDE_CODE_START_HERE.md) | Instrução de entrada para ler, pesquisar e executar sem contexto oral |
| [16 — Limites e confiabilidade da IA](16_PRINCIPIOS_DE_CONFIABILIDADE_E_LIMITES_DA_IA.md) | O que pode e não pode ser garantido |
| [17 — Rig, anatomia e orientação](17_VALIDACAO_DE_RIG_ANATOMIA_E_ORIENTACAO.md) | Convenções semânticas, esquerda/direita, poses sentinela e validação |
| [18 — Animação e continuidade](18_VALIDACAO_DE_ANIMACAO_E_CONTINUIDADE.md) | Foot contact, foot sliding, loops e validação temporal |
| [19 — Testes visuais](19_TESTES_VISUAIS_GOLDEN_IMAGES_E_QA.md) | Alpha, recorte, pivot, golden images e regressão |
| [20 — Quality Gates](20_QUALITY_GATES_E_APROVACAO.md) | Aprovação automática e humana |
| [21 — Pesquisa e fontes](21_PESQUISA_TECNICA_E_REFERENCIAS.md) | Documentação oficial e regras de pesquisa na web |
| [22 — Execução autônoma](22_PLANO_AUTONOMO_DE_EXECUCAO_CLAUDE_CODE.md) | Plano de execução de ponta a ponta |
| [23 — Matriz de testes](23_MATRIZ_DE_TESTES_E_EVIDENCIAS.md) | Cobertura e evidências obrigatórias |

## Como usar esta documentação

1. Entregue a pasta inteira ao Claude Code e mande ler `CLAUDE_CODE_START_HERE.md`; este arquivo contém a ordem de leitura e a missão autônoma.
2. Leia `00_SUMARIO_E_DECISOES.md` e `01_VISAO_E_ESCOPO.md` para entender o produto.
3. Use `04_ARQUITETURA_TECNICA.md`, `05_ESPECIFICACAO_MODULOS.md` e `06_CONTRATOS_DE_DADOS.md` como referência de engenharia.
4. Implemente o vertical slice descrito em `12_MVP_E_CRITERIOS_DE_ACEITE.md` antes de construir a interface completa.
5. Use os documentos 16–23 para validar os aspectos técnicos, visuais e de autonomia do agente.

## Convenções importantes

- **Decisão:** escolha consolidada nesta proposta.
- **Proposta:** solução recomendada, sujeita a validação técnica.
- **A validar:** ponto que exige protótipo, medição ou decisão posterior.
- Os exemplos JSON são contratos iniciais ilustrativos. Antes de produção, devem ser transformados em schemas formais versionados e testados.
- Não interpretar o roadmap como promessa de prazo. A duração de cada fase depende de testes com Blender, rigs, qualidade visual e capacidade de hardware.

## Princípio central

> A IA sugere e auxilia; o usuário aprova; o sistema constrói e valida; o Blender renderiza; o Exporter entrega; o Godot consome.

## Limite importante

Esta documentação não promete eliminar todos os defeitos de IA. Ela estabelece uma arquitetura em que IA gera referências e auxilia decisões, enquanto geometria 3D, rigs semânticos, animações estruturadas, renderização determinística, testes e revisão humana controlam a produção. A geração livre e automática de qualquer malha 3D a partir de uma imagem não faz parte do MVP.
