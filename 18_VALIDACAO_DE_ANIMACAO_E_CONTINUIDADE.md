# 18 — Validação de animação e continuidade temporal

## 1. Objetivo

Garantir que animações não sejam apenas uma sequência de imagens. Elas precisam representar um movimento contínuo, coerente com o rig, com contatos de pés, pivô estável e direção correta.

## 2. Animação como dado estruturado

Cada ação deve declarar:

- `animation_id`;
- rig compatível e versão;
- FPS;
- frame inicial e final;
- duração;
- loop ou não;
- pose inicial e final esperadas;
- eventos semânticos por frame/intervalo;
- perfil de tolerâncias;
- direções para renderização;
- estado de aprovação.

Os eventos são parte do contrato, por exemplo:

```json
{
  "animation_id": "walk",
  "fps": 12,
  "loop": true,
  "events": [
    {"frame": 0, "event": "LEFT_FOOT_CONTACT"},
    {"frame": 4, "event": "RIGHT_FOOT_CONTACT"}
  ]
}
```

Este JSON é ilustrativo; os frames de contato devem ser definidos pela animação efetivamente produzida e não assumidos universalmente.

## 3. Testes obrigatórios

### 3.1 Avaliação de todos os frames

O pipeline deve avaliar a pose do rig em cada frame exportado, e não somente no primeiro e último. Registrar transform de root, pelvis, pés, mãos e cabeça nos pontos de inspeção.

### 3.2 Foot contact e foot sliding

Durante intervalos de apoio:

- o pé de apoio deve permanecer próximo ao plano de chão;
- a velocidade horizontal do ponto de apoio deve ficar abaixo da tolerância do perfil;
- não pode haver deslocamento abrupto do root sem regra de root motion;
- o pé oposto deve executar a fase de balanço.

As tolerâncias devem ser expressas em relação à altura do personagem ou escala normalizada e calibradas com o primeiro rig. Registrar a unidade e o perfil usado. Não inventar um valor único para qualquer personagem.

### 3.3 Ground penetration e floating

Verificar a posição dos pontos de contato em relação ao plano de chão. Detectar penetração e flutuação excessivas. O teste deve considerar calçados, patas, flutuação intencional e criaturas voadoras por perfil.

### 3.4 Continuidade temporal

Entre frames adjacentes, medir:

- deslocamento dos landmarks semânticos;
- mudança de orientação;
- mudança de bounding box da silhueta;
- deslocamento do pivot;
- diferença de pixels/silhueta;
- aceleração/variação de movimento quando disponível.

Não exigir diferença visual mínima entre todos os frames: um quadro de contato pode legitimamente repetir a silhueta. Os limites são por ação e por perfil, calibrados com exemplos aprovados.

### 3.5 Loop

Para ações em loop:

- comparar pose e posição no último/primeiro instante;
- verificar root displacement;
- verificar velocidade/tangente de transição;
- avaliar o loop em playback, não apenas comparar duas imagens;
- produzir preview animado para revisão.

### 3.6 Integridade da animação

- nenhuma pose contém NaN/Inf;
- todas as ações referenciam rig existente;
- duração e FPS são positivos e compatíveis;
- nenhum frame obrigatório ausente;
- o render de cada direção contém o número de frames esperado;
- nenhuma imagem tem zero pixels visíveis por falha inesperada.

## 4. Oito direções

Cada ação precisa gerar as oito direções sob a mesma convenção. A direção é metadado, não parte inferida a partir do nome do arquivo depois da renderização.

A renderização deve usar a câmera de jogo fixa e girar o root do personagem em headings definidos pelo perfil, ou um método equivalente matematicamente testado. Escolher um método único no MVP. Não misturar câmera orbitando e personagem girando dentro do mesmo lote sem conversão explícita.

## 5. Inspeção de oclusão

A profundidade e a oclusão devem vir do z-buffer da cena 3D. A imagem 2D não deve tentar decidir por uma regra simples qual perna desenhar por cima em cada frame. Gerar uma folha de diagnóstico com cores/labels de membro para confirmar a ordenação.

## 6. Relatório por animação

Cada ação deve gerar:

- `animation_validation.json`;
- contact sheet por direção;
- preview animado ou vídeo de QA;
- métricas de foot contact;
- métricas de loop;
- lista de warnings/failures;
- versão do rig, Blender e RenderProfile.

## 7. Critério de aceite

Uma animação só passa quando integridade estrutural, contatos, limites, continuidade, oito direções e revisão visual exigida tiverem sido concluídos. Uma animação que renderiza sem erro ainda não está validada.
