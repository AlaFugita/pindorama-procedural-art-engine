# 13 — Riscos e decisões abertas

## 1. Riscos técnicos

| Risco | Impacto | Mitigação |
|---|---|---|
| IA gerar conceito impossível de montar com biblioteca | Alto | Traduzir para atributos suportados e marcar diferenças não atendidas |
| Biblioteca modular limitada | Alto | Criar kit inicial bem definido e roadmap de expansão |
| Peças incompatíveis entre corpos | Alto | Metadados de compatibilidade, ancoragens e testes |
| Rig inadequado para acessórios/roupas | Alto | Regras de deformação e revisão por animação |
| Desalinhamento entre direções | Alto | Canvas fixo, pivô e testes de regressão |
| Render lento | Médio/alto | Benchmark, cache e concorrência controlada |
| Arquivos grandes | Médio | Atlas, compressão e política de resolução |
| Empacotamento Python/Blender complexo | Médio/alto | Prova de conceito de instalação ainda na fundação |
| API local insegura | Alto | Loopback, autenticação local e processo supervisionado |
| Mudança de versão do Blender/Godot | Médio | Fixar versões por release e testar atualizações separadamente |

## 2. Risco de expectativa sobre IA

Uma descrição textual arbitrária não garante que exista um modelo 3D pronto e compatível. No MVP, o sistema deve selecionar e combinar componentes conhecidos. Text-to-3D, geração de malha e retopologia automática são linhas futuras de pesquisa, não pressupostos do pipeline principal.

## 3. Licenças e direitos

Registrar:
- origem de cada modelo 3D;
- licença de texturas e materiais;
- licença de fontes e bibliotecas;
- provider e modelo de IA;
- termos aplicáveis à saída gerada;
- referências culturais e visuais;
- autorizações necessárias.

Não incluir assets de terceiros na biblioteca do produto sem verificar autorização de uso e redistribuição.

## 4. Decisões abertas

| ID | Questão | Quando decidir |
|---|---|---|
| DA-001 | Resolução padrão de frame | Durante primeiro render benchmark |
| DA-002 | Projeção isométrica estrita ou ângulo estilizado | Após teste visual com cenário do jogo |
| DA-003 | Câmera orbitando ou modelo girando | Durante protótipo de oito direções |
| DA-004 | Atlas por direção ou layout consolidado | Após teste de importação Godot |
| DA-005 | FPS e frames por animação | Durante criação do pacote de animação |
| DA-006 | Provider de IA inicial | Após teste de qualidade, custo e licença |
| DA-007 | Blender empacotado ou dependência externa instalada | Durante prova de empacotamento Windows |
| DA-008 | Uso de modelo local para concept art | Após avaliação de hardware e qualidade |
| DA-009 | Estratégia de backup e biblioteca pesada | Antes de distribuir versão pública |

## 5. Política de decisão

Cada decisão significativa deve registrar:
- contexto;
- opções avaliadas;
- escolha;
- justificativa;
- consequências;
- data e responsável;
- status (proposta, aprovada, substituída).

## 6. Recomendação de controle de escopo

Não iniciar uma família de criatura antes de o fluxo humanoide estar validado de ponta a ponta. Não investir em geração arbitrária de malha por IA antes de saber se a biblioteca modular atende a maioria dos personagens prioritários.

## 7. Adendo de 2026-11-06

| ID | Estado |
|---|---|
| Risco: rosto e cabelo não atingirem o padrão por código | Materializado na Rota A; pode exigir escultura humana |
| DA-006 / DA-008 | D4 e D5: só local e sem custo nesta etapa |

## 8. Adendo de 2026-11-07: riscos do Procedural Art Engine

- **Teto de qualidade procedural:** primitivas e lofts podem não chegar à riqueza da Duende. Mitigação: geometria mais rica (subdivisão, campos de distância) e composição por passes. Pela regra 8, se não chegar, isso será dito.
- **Expansão prematura:** abrir domínios antes de o personagem estar aprovado. Mitigação: o §17 e o roadmap.
- **Memória do MMORPG:** veja `docs/DETALHAMENTO_ARTISTICO.md` §5. Atlas recortado é pré-requisito para escala.
- **Decisões abertas:** estilo principal (suave × pixel), resolução de referência, revogação de D2, aprovação do G9. Conflitos C1 a C6 em [docs/audit/MATRIZ_ADERENCIA_PROCEDURAL_ART_ENGINE_2026-11-07.md](docs/audit/MATRIZ_ADERENCIA_PROCEDURAL_ART_ENGINE_2026-11-07.md).
