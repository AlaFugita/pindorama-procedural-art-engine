# 17 — Validação de rig, anatomia e orientação

## 1. Pergunta que este documento responde

Como o software sabe se a perna esquerda é realmente a perna esquerda, qual pé está à frente, se o braço pertence ao lado correto e se oito direções não foram trocadas?

A resposta não pode depender de olhar pixels isolados. A resposta vem da combinação de coordenadas canônicas, nomenclatura semântica, hierarquia de ossos, posições conhecidas, poses sentinela e projeção 3D.

## 2. Coordenadas canônicas do projeto

Adotar uma convenção interna única e documentada:

- sistema destro;
- `+Z` = cima;
- `+Y` = frente do personagem;
- `+X` = lado direito anatômico do personagem;
- `-X` = lado esquerdo anatômico do personagem;
- origem do personagem = centro entre os apoios dos pés, no plano do chão;
- unidade de trabalho = metro;
- yaw do personagem = rotação em torno de `Z`.

**Atenção:** `LEFT` e `RIGHT` são sempre do ponto de vista do próprio personagem, nunca do observador da imagem. Em uma vista frontal, a mão esquerda anatômica aparece à direita de quem observa.

A exportação glTF exige uma conversão de eixos explícita. A especificação glTF define `+Y` como up, `+Z` como frente e `-X` como direita. Com a convenção interna acima, o adaptador pode converter `(x, y, z)` interno para `(-x, z, y)` em glTF, desde que a transformação seja aplicada consistentemente a geometria, armature, câmera, normais, transforms e animações e seja coberta por teste. Não espalhar conversões de eixo pelo código.

## 3. Direções de sprite

Definir IDs estáveis e ordem oficial:

`N, NE, E, SE, S, SW, W, NW`.

A tabela de yaw deve ser centralizada em `DirectionConvention`, não repetida em scripts:

| ID | Direção de mundo | Yaw |
|---|---|---|
| N | vetor de frente definido pelo mapa do jogo | configurado no perfil |
| NE | diagonal entre N e E | configurado no perfil |
| E | vetor leste | configurado no perfil |
| SE | diagonal entre S e E | configurado no perfil |
| S | vetor oposto ao N | configurado no perfil |
| SW | diagonal entre S e W | configurado no perfil |
| W | vetor oeste | configurado no perfil |
| NW | diagonal entre N e W | configurado no perfil |

Não fixar a correspondência entre norte do mapa e `+Y` sem documentar a convenção do jogo. A configuração deve declarar qual heading representa a pose frontal canônica. Testar todos os oito headings e salvar uma folha de inspeção com rótulos visíveis.

## 4. Rig semântico humanoide

O MVP deverá usar um rig de referência com nomes estáveis. Nomes sugeridos:

```text
root
└── pelvis
    ├── spine_01
    │   └── chest
    │       ├── neck
    │       │   └── head
    │       ├── clavicle_l -> upper_arm_l -> forearm_l -> hand_l
    │       └── clavicle_r -> upper_arm_r -> forearm_r -> hand_r
    ├── thigh_l -> shin_l -> foot_l -> toe_l
    └── thigh_r -> shin_r -> foot_r -> toe_r
```

O rig pode conter controles, pole targets, IK helpers e twists extras. Esses ossos devem ser distinguidos dos ossos deformadores e documentados em `RigProfile`.

Cada osso semântico precisa declarar:

- `semantic_id`;
- `side`: `LEFT`, `RIGHT`, `CENTER` ou `NONE`;
- `role`: `upper_leg`, `lower_leg`, `foot`, etc.;
- nome real no Blender;
- pai esperado;
- se deforma malha;
- grupo de vértices esperado;
- limites/constraints do perfil;
- versão do rig.

Não depender apenas do sufixo do nome. O manifesto semântico deve ser explícito e validado.

## 5. Como validar a perna correta

Implementar uma sequência de testes determinísticos:

### 5.1 Existência e hierarquia

- todos os ossos obrigatórios existem;
- IDs semânticos não se repetem;
- ossos esquerdo/direito existem em pares no rig humanoide padrão;
- `thigh_l` pertence à cadeia esquerda e `thigh_r` à direita;
- joelho e pé descendem da coxa correspondente;
- pais, conexões e deform flags são válidos.

### 5.2 Posição na pose de repouso

Converter cabeças e caudas dos ossos para o espaço canônico do personagem. Os principais ossos do lado esquerdo devem estar do lado `-X` e do lado direito no `+X`, com tolerância configurada. Não usar coordenadas locais de osso sem transformá-las para o espaço correto.

Corpos assimétricos são permitidos. A regra valida a identidade semântica, não obriga a malha a ser simétrica.

### 5.3 Poses sentinela

Criar uma cena de teste com marcadores coloridos não exportados:

- marcador verde no punho anatômico esquerdo;
- marcador azul no punho anatômico direito;
- marcador magenta no tornozelo esquerdo;
- marcador amarelo no tornozelo direito;
- eixos `+X`, `+Y`, `+Z` visíveis.

Executar uma pose por vez: mover/rotacionar apenas o controle da perna esquerda e confirmar que o membro esquerdo se move; repetir para direita, braços, cabeça e coluna. Capturar render de debug e relatório de transformação. Marcadores são instrumentação de QA, removida das exportações de produção.

### 5.4 Projeção para a tela

Projetar os pontos anatômicos com a matriz da câmera. Comparar as posições previstas dos marcadores com os pixels/landmarks detectados. Para cada uma das oito direções, salvar o mapa esperado de projeção. A troca esquerda/direita deve falhar o teste, mesmo que a silhueta geral pareça bonita.

## 6. Anatomia: o que é verificável

O software pode verificar automaticamente:

- presença e conectividade da hierarquia;
- proporções entre segmentos em relação ao perfil;
- pesos de skinning e vértices sem influência;
- deformação em poses de teste;
- limites articulares configurados;
- interseções grosseiras por volumes de colisão/proxies;
- alinhamento dos pés com o plano do chão;
- mapeamento de marcadores semânticos.

O software não deve alegar que essas verificações comprovam anatomia perfeita. Estilo chibi, criaturas e anatomias fantásticas podem divergir deliberadamente de proporções humanas. Os critérios precisam ser definidos por família de rigs e por perfil artístico.

## 7. Skinning e deformação

Validar:

- todos os vértices deformáveis têm pelo menos uma influência;
- soma dos pesos dentro da tolerância configurada;
- limite de influências por vértice compatível com o destino;
- grupos de vértices correspondem aos ossos documentados;
- sem pesos atribuídos a osso inexistente;
- deformação de ombro, cotovelo, quadril, joelho e tornozelo em poses sentinela;
- ausência de NaN/Inf em transforms e posições avaliadas.

Não impor números universais de peso ou ângulo a todas as espécies. Os limites devem estar em profiles versionados, com defaults derivados do rig-base e calibrados por testes.

## 8. Qual é a “perna da frente”?

Não existe uma identidade anatômica chamada simplesmente “perna da frente” em um humanoide bípede. Há perna esquerda e direita. A perna que parece mais próxima da câmera muda conforme heading, pose e projeção. O software deve calcular a profundidade/oclusão a partir da cena 3D e não renomear o membro com base no desenho 2D.

Para caminhada, usar eventos de contato: `LEFT_FOOT_CONTACT`, `RIGHT_FOOT_CONTACT`, `LEFT_SWING`, `RIGHT_SWING`. O estado de apoio é determinado pelo ciclo de animação e pelo contato com o solo, não por adivinhação visual da IA.

## 9. Critério de aceite do rig humanoide

O rig não é aprovado até:

- hierarquia e IDs semânticos passarem;
- os testes sentinela movimentarem o membro correto;
- os marcadores esquerdo/direito aparecerem na posição projetada esperada em oito direções;
- poses de deformação não exibirem falhas graves;
- pesos e constraints estarem dentro do perfil;
- uma pessoa revisar a folha de poses e confirmar visualmente o resultado.
