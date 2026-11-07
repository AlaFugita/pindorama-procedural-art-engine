# 20 — Quality Gates e fluxo de aprovação

## 1. Objetivo

Impedir que uma etapa defeituosa contamine todo o restante do pipeline. Cada fase tem critérios objetivos e um estado de revisão.

## 2. Portões de qualidade

| Gate | Etapa | Passagem obrigatória |
|---|---|---|
| G0 | Ambiente | Versões e ferramentas detectadas; smoke tests executados |
| G1 | CharacterSpec | Schema válido, IDs e referências existentes |
| G2 | Concept | Referência aprovada por pessoa; proveniência/licença registrada |
| G3 | 3D Build | Objetos, materiais, escala, componentes e silhueta validados |
| G4 | Rig | Hierarquia, semântica, poses sentinela e deformação aprovadas |
| G5 | Animation | Contatos, limites, loop e continuidade validados |
| G6 | Render | Oito direções, câmera, alpha, pivot e dimensões aprovados |
| G7 | Export | Manifesto, arquivos e metadados íntegros |
| G8 | Runtime | Godot importa e reproduz as ações/direções corretas |
| G9 | Art Approval | Revisão final de conceito, consistência e qualidade visual |

## 3. Hard fail vs revisão

### Hard fail

- contrato inválido;
- rig obrigatório ausente;
- lado anatômico trocado nos testes sentinela;
- frame obrigatório ausente;
- export fora das dimensões/formatos declarados;
- personagem cortado;
- alpha inválido quando exigido;
- Godot não carrega ou não reproduz a animação;
- arquivos não rastreáveis ou erro de licença conhecido.

### Review humano

- correspondência com o concept;
- qualidade do desenho/modelagem;
- leitura da silhueta em escala de jogo;
- gosto artístico e direção de arte;
- relevância cultural de referências específicas;
- deformações aceitáveis em estilo estilizado;
- qualidade final de animação.

## 4. Status e transições

Cada gate registra `PENDING`, `PASS`, `WARN`, `FAIL`, `REVIEW`, `APPROVED`, `REJECTED` ou `NOT_TESTED`. Não permitir que `NOT_TESTED`, `FAIL` ou `REJECTED` avancem como aprovado.

## 5. Aprovação humana enxuta

A pessoa não deve ser solicitada a revisar cada quadro individualmente quando uma folha de contato e um preview representativo forem suficientes. Entretanto, o sistema deve expor zoom, reprodução e seleção de qualquer frame/direção para investigar alertas.

Pontos humanos obrigatórios no MVP:

1. aprovação do primeiro concept;
2. aprovação do primeiro modelo 3D e silhueta;
3. aprovação da folha de poses sentinela;
4. aprovação de idle/walk nas oito direções;
5. aprovação do resultado dentro do Godot.

Após um perfil-base ser aprovado, variações que não alteram rig, estrutura ou regras artísticas podem utilizar revisão reduzida. A decisão e o motivo precisam ficar registrados.

## 6. Proveniência e reprodutibilidade

Cada aprovação deve registrar:

- usuário/revisor ou identificador local;
- timestamp;
- versão do CharacterSpec;
- hash dos assets;
- versão dos modelos/workflows IA, se houver;
- versão Blender e do aplicativo;
- RenderProfile;
- relatório de testes;
- comentário/decisão.

## 7. Política de export

- `experimental`: pode ser criado com warnings, mas sempre marcado como não aprovado;
- `review`: todos os testes automáticos passaram, mas há revisão humana pendente;
- `production`: todos os gates obrigatórios passaram e aprovações requeridas foram registradas.

Nunca rotular um asset como `production` apenas porque foi renderizado.

## 8. Adendo de 2026-11-06 — gate G3M

Decisão do usuário: entre G3 e G4 existe o gate **G3M (Personagem Mestre)**. Nenhuma animação avançada avança antes dele. Critérios técnicos, visuais e funcionais em `docs/MASTER_QUALITY_CRITERIA.md`. A aprovação é sempre humana, e reprovações anteriores permanecem no histórico.
