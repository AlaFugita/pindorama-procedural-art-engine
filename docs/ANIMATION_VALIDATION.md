# Validação das animações

**Gerado em:** 2026-11-07 por `scripts/build_animation_report.py`, a partir dos testes executados.
**Página:** [animations.html](../animations.html), com filtros, as 8 direções lado a lado e os detalhes de cada animação.

## Como o status é calculado

| Status | Regra |
|---|---|
| PASS | Gates do clip aprovados (G5: IK, contato, deslizamento, laço, chão; G6: imagem) **e** o Godot importou, tocou na velocidade e na sequência certas **e** os cenários de estado com essa ação passaram |
| WARN | Funciona, com ressalva medida (ex.: quadros repetidos acidentais, coxa a mais de 15 mm da túnica) |
| FAIL | Algum check do clip falhou nos gates ou no Godot |
| MISSING | Ação do catálogo sem clip implementado |
| NOT TESTED | Clip existe, mas o Godot não rodou para esse personagem |

Um GIF existir **não** muda o status.

## Aprendiz suave 192 (`aprendiz_suave_192`, isometric_smooth_192_v1)

Godot: 4.7.2-stable (official)

### Matriz de cobertura

| Categoria | Ação | Clip | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|---|---|
| Locomoção | Idle | `idle` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Locomoção | Walking | `walk` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Locomoção | Running | `run` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Locomoção | Falling | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Locomoção | Landing | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Locomoção | Jumping | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Corpo a corpo | Melee Attack | `attack_melee` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Corpo a corpo | Ataque com arma equipada | `attack_melee` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Corpo a corpo | Ataques por tipo de arma | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Corpo a corpo | Sequência de ataques | `attack_melee` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| À distância | Shooting | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Aiming | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Throwing | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Lançamento de projéteis | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Recuperação após disparo | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Magia | Magic Casting | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Preparação da magia | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Execução do lançamento | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Recuperação após lançamento | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Habilidades especiais | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Interacting | `interact` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Interação | Coletar objetos | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Utilizar objetos | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Abrir/manipular cenário | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Interagir com NPCs | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Utilizar equipamentos | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Estados | Taking Damage | `hurt` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Estados | Stunned | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Estados | Death | `death` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Estados | Respawn | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |

### Clips implementados

| Clip | Categoria | FPS | Quadros | Duração | Laço | Prioridade | Interrompível | Volta para | Fases | Problemas |
|---|---|---|---|---|---|---|---|---|---|---|
| `idle` | locomotion | 8 | 8 | 1.00s | sim | 0 | 0 | terminal | — | ANI-REVIEW:idle: qualidade do movimento exige revisão humana; IMG-005:idle: 3 frames repetidos dentro de uma direção |
| `walk` | locomotion | 12 | 8 | 0.67s | sim | 0 | 0 | terminal | — | ANI-REVIEW:walk: qualidade do movimento exige revisão humana |
| `run` | locomotion | 16 | 8 | 0.50s | sim | 0 | 0 | terminal | — | ANI-REVIEW:run: qualidade do movimento exige revisão humana |
| `attack_melee` | melee | 12 | 8 | 0.67s | não | 10 | 5 | idle | prepare 0–2, execute 3–4, recover 5–7 | ANI-REVIEW:attack_melee: qualidade do movimento exige revisão humana |
| `cast` | magic | 12 | 12 | 1.00s | não | 10 | 8 | idle | prepare 0–5, execute 6–7, recover 8–11 | ANI-REVIEW:cast: qualidade do movimento exige revisão humana; ANI-005:cast: ponto mais baixo +0.5 mm (boot_sole_l, quadro 11); coxa fora da túnica até 15.8 mm |
| `interact` | interaction | 10 | 8 | 0.80s | não | 10 | 6 | idle | prepare 0–2, execute 3–5, recover 6–7 | ANI-REVIEW:interact: qualidade do movimento exige revisão humana |
| `hurt` | state | 12 | 6 | 0.50s | não | 20 | 3 | idle | execute 0–1, recover 2–5 | ANI-REVIEW:hurt: qualidade do movimento exige revisão humana |
| `death` | state | 10 | 10 | 1.00s | não | 100 | 99 | terminal | execute 0–7, hold 8–9 | ANI-REVIEW:death: qualidade do movimento exige revisão humana |

### Cenários de estado executados no Godot (GODOT-003)

| Cenário | Ações | Status | Resultado |
|---|---|---|---|
| clip:idle | idle | PASS | 8 quadros a 8 fps (1.00s), 8 direções no SpriteFrames, sequência completa |
| clip:walk | walk | PASS | 8 quadros a 12 fps (0.67s), 8 direções no SpriteFrames, sequência completa |
| clip:run | run | PASS | 8 quadros a 16 fps (0.50s), 8 direções no SpriteFrames, sequência completa |
| clip:attack_melee | attack_melee | PASS | 8 quadros a 12 fps (0.67s), 8 direções no SpriteFrames, sequência completa |
| clip:cast | cast | PASS | 12 quadros a 12 fps (1.00s), 8 direções no SpriteFrames, sequência completa |
| clip:interact | interact | PASS | 8 quadros a 10 fps (0.80s), 8 direções no SpriteFrames, sequência completa |
| clip:hurt | hurt | PASS | 6 quadros a 12 fps (0.50s), 8 direções no SpriteFrames, sequência completa |
| clip:death | death | PASS | 10 quadros a 10 fps (1.00s), 8 direções no SpriteFrames, sequência completa |
| idle→walk→run→idle | idle, walk, run | PASS | histórico ["walk", "run", "idle"] |
| attack_melee: idle→ação→idle | attack_melee | PASS | dura 0.67s e volta para idle |
| cast: idle→ação→idle | cast | PASS | dura 1.00s e volta para idle |
| interact: idle→ação→idle | interact | PASS | dura 0.80s e volta para idle |
| hurt: idle→ação→idle | hurt | PASS | dura 0.50s e volta para idle |
| andar + atacar | walk, attack_melee | PASS | termina em walk |
| correr + atacar | run, attack_melee | PASS | termina em run |
| atacar e virar | attack_melee | PASS | quadro 2 mantido, clip attack_melee_W |
| magia + movimento | cast, walk | PASS | preparo protegido; corta a recuperação a partir do quadro 8 |
| interagir em movimento | walk, interact | PASS | termina em walk |
| dano interrompe ataque | attack_melee, hurt | PASS | histórico ["attack_melee", "hurt", "idle"] |
| ataque durante dano | hurt, attack_melee | PASS | estado hurt |
| dois ataques seguidos | attack_melee | PASS | histórico ["attack_melee", "attack_melee"] |
| morte é terminal | death | PASS | quadro final 9, estado death |

## Aprendiz suave arma (`aprendiz_suave_var_arma`, isometric_smooth_192_v1)

Godot: 4.7.2-stable (official)

### Matriz de cobertura

| Categoria | Ação | Clip | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|---|---|
| Locomoção | Idle | `idle` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Locomoção | Walking | `walk` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Locomoção | Running | `run` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Locomoção | Falling | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Locomoção | Landing | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Locomoção | Jumping | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Corpo a corpo | Melee Attack | `attack_melee` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Corpo a corpo | Ataque com arma equipada | `attack_melee` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Corpo a corpo | Ataques por tipo de arma | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Corpo a corpo | Sequência de ataques | `attack_melee` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| À distância | Shooting | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Aiming | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Throwing | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Lançamento de projéteis | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| À distância | Recuperação após disparo | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Magia | Magic Casting | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Preparação da magia | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Execução do lançamento | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Recuperação após lançamento | `cast` | WARN | WARN | WARN | WARN | WARN | WARN | WARN | WARN |
| Magia | Habilidades especiais | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Interacting | `interact` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Interação | Coletar objetos | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Utilizar objetos | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Abrir/manipular cenário | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Interagir com NPCs | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Interação | Utilizar equipamentos | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Estados | Taking Damage | `hurt` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Estados | Stunned | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Estados | Death | `death` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Estados | Respawn | `—` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |

### Clips implementados

| Clip | Categoria | FPS | Quadros | Duração | Laço | Prioridade | Interrompível | Volta para | Fases | Problemas |
|---|---|---|---|---|---|---|---|---|---|---|
| `idle` | locomotion | 8 | 8 | 1.00s | sim | 0 | 0 | terminal | — | ANI-REVIEW:idle: qualidade do movimento exige revisão humana; IMG-005:idle: 3 frames repetidos dentro de uma direção |
| `walk` | locomotion | 12 | 8 | 0.67s | sim | 0 | 0 | terminal | — | ANI-REVIEW:walk: qualidade do movimento exige revisão humana |
| `run` | locomotion | 16 | 8 | 0.50s | sim | 0 | 0 | terminal | — | ANI-REVIEW:run: qualidade do movimento exige revisão humana |
| `attack_melee` | melee | 12 | 8 | 0.67s | não | 10 | 5 | idle | prepare 0–2, execute 3–4, recover 5–7 | ANI-REVIEW:attack_melee: qualidade do movimento exige revisão humana |
| `cast` | magic | 12 | 12 | 1.00s | não | 10 | 8 | idle | prepare 0–5, execute 6–7, recover 8–11 | ANI-REVIEW:cast: qualidade do movimento exige revisão humana; ANI-005:cast: ponto mais baixo +0.5 mm (boot_sole_l, quadro 11); coxa fora da túnica até 15.8 mm |
| `interact` | interaction | 10 | 8 | 0.80s | não | 10 | 6 | idle | prepare 0–2, execute 3–5, recover 6–7 | ANI-REVIEW:interact: qualidade do movimento exige revisão humana |
| `hurt` | state | 12 | 6 | 0.50s | não | 20 | 3 | idle | execute 0–1, recover 2–5 | ANI-REVIEW:hurt: qualidade do movimento exige revisão humana |
| `death` | state | 10 | 10 | 1.00s | não | 100 | 99 | terminal | execute 0–7, hold 8–9 | ANI-REVIEW:death: qualidade do movimento exige revisão humana |

### Cenários de estado executados no Godot (GODOT-003)

| Cenário | Ações | Status | Resultado |
|---|---|---|---|
| clip:idle | idle | PASS | 8 quadros a 8 fps (1.00s), 8 direções no SpriteFrames, sequência completa |
| clip:walk | walk | PASS | 8 quadros a 12 fps (0.67s), 8 direções no SpriteFrames, sequência completa |
| clip:run | run | PASS | 8 quadros a 16 fps (0.50s), 8 direções no SpriteFrames, sequência completa |
| clip:attack_melee | attack_melee | PASS | 8 quadros a 12 fps (0.67s), 8 direções no SpriteFrames, sequência completa |
| clip:cast | cast | PASS | 12 quadros a 12 fps (1.00s), 8 direções no SpriteFrames, sequência completa |
| clip:interact | interact | PASS | 8 quadros a 10 fps (0.80s), 8 direções no SpriteFrames, sequência completa |
| clip:hurt | hurt | PASS | 6 quadros a 12 fps (0.50s), 8 direções no SpriteFrames, sequência completa |
| clip:death | death | PASS | 10 quadros a 10 fps (1.00s), 8 direções no SpriteFrames, sequência completa |
| idle→walk→run→idle | idle, walk, run | PASS | histórico ["walk", "run", "idle"] |
| attack_melee: idle→ação→idle | attack_melee | PASS | dura 0.67s e volta para idle |
| cast: idle→ação→idle | cast | PASS | dura 1.00s e volta para idle |
| interact: idle→ação→idle | interact | PASS | dura 0.80s e volta para idle |
| hurt: idle→ação→idle | hurt | PASS | dura 0.50s e volta para idle |
| andar + atacar | walk, attack_melee | PASS | termina em walk |
| correr + atacar | run, attack_melee | PASS | termina em run |
| atacar e virar | attack_melee | PASS | quadro 2 mantido, clip attack_melee_W |
| magia + movimento | cast, walk | PASS | preparo protegido; corta a recuperação a partir do quadro 8 |
| interagir em movimento | walk, interact | PASS | termina em walk |
| dano interrompe ataque | attack_melee, hurt | PASS | histórico ["attack_melee", "hurt", "idle"] |
| ataque durante dano | hurt, attack_melee | PASS | estado hurt |
| dois ataques seguidos | attack_melee | PASS | histórico ["attack_melee", "attack_melee"] |
| morte é terminal | death | PASS | quadro final 9, estado death |

## Testes do Godot realizados

| ID | O que verifica | Onde |
|---|---|---|
| GODOT-001 | Importação: cada clip nas 8 direções, contagem de quadros, FPS e modo de laço iguais ao manifesto; pixels importados idênticos ao PNG; alpha preservado; região de cada quadro | `smoke_test.gd` (headless) |
| GODOT-002 | Reprodução real com janela: `AnimatedSprite2D` toca os clips, a tela capturada bate com o quadro esperado (posição e pivô) | captura + `godot_bridge.compare_captures` |
| GODOT-003 | Máquina de estados com o pacote real: sequência de quadros completa e em ordem no tempo de jogo, duração, retorno ao estado certo, andar/correr + atacar, virar no meio da ação, magia + movimento, interagir em movimento, dano interrompendo ataque, ataque recusado durante o dano, dois ataques em fila, morte terminal | `state_test.gd` + `ics_anim_controller.gd` |

## Regras de prioridade e interrupção (implementadas em `IcsAnimController`)

- Locomoção (idle, walk, run): prioridade 0; segue o movimento e a direção.
- Ação sem laço (ataque, magia, interação): prioridade 10; toca até o fim e volta para `return_to`, ou para walk/run se ainda há movimento.
- Prioridade **maior** interrompe a qualquer momento: dano (20) corta ação; morte (100) corta tudo.
- Movimento ou ação de **mesma** prioridade só corta a partir de `interruptible_after`. Antes disso, o pedido de ação fica numa fila de um item, que gera o combo de 2.
- Mudar de direção durante a ação troca o clip da direção **sem reiniciar** o quadro.
- Morte é terminal: `return_to` vazio; nada mais é aceito.
- A movimentação do jogo não é bloqueada pelo controlador. O jogo deve parar o deslocamento durante ações de prioridade ≥ 10 (as ações são `in_place`).

## Animações ausentes (MISSING)

- **Locomoção / Falling**: Exige deslocamento vertical da raiz; o pipeline é in_place
- **Locomoção / Landing**: Depende de Falling
- **Locomoção / Jumping**: Exige raiz com altura (root motion vertical) e evento de decolagem
- **Corpo a corpo / Ataques por tipo de arma**: Espada, maça, lança e duas mãos precisam de WeaponProfile
- **À distância / Shooting**: Não há arco nem arma de disparo no personagem
- **À distância / Aiming**
- **À distância / Throwing**
- **À distância / Lançamento de projéteis**: Evento existe só em CAST_RELEASE; sem projétil
- **À distância / Recuperação após disparo**
- **Magia / Habilidades especiais**
- **Interação / Coletar objetos**: Pode reutilizar interact; sem clip próprio (abaixar até o chão)
- **Interação / Utilizar objetos**
- **Interação / Abrir/manipular cenário**
- **Interação / Interagir com NPCs**: Pode reutilizar interact ou idle; sem clip próprio
- **Interação / Utilizar equipamentos**
- **Estados / Stunned**
- **Estados / Respawn**

## Problemas encontrados

1. **Magia (`cast`) em WARN:** a coxa sai até 15,8 mm da túnica no lançamento (limite de aviso: 15 mm). Invisível nas vistas frontais, mas medido. Abrir a barra da túnica ou reduzir a inclinação.
2. **Idle em WARN (IMG-005):** 3 quadros repetidos por direção. São fases simétricas do ciclo de respiração (cos 2θ). É uma repetição acidental, não marcada em `held_frames`.
3. **Corrigidos nesta etapa:**
   - morte com o cajado 82 mm abaixo do chão, achada pelo ANI-005;
   - quadro inicial = final em todas as ações (engasgo na volta ao idle);
   - dano começando em pose neutra.
4. **Sem bloqueio de deslocamento:** as ações são `in_place`. O jogo precisa travar o movimento durante a ação; isso é regra documentada, não aplicada pelo pacote.
5. **Mesmo clip para variações de interação** (coletar, NPC, usar): marcadas como MISSING; hoje só existe `interact` genérico.

## Plano de correção priorizado

| Pri. | Item | Por quê | Esforço |
|---|---|---|---|
| P1 | Ajustar `cast` (coxa) e marcar ou corrigir as repetições do idle | Zerar os WARN atuais | Baixo |
| P1 | `WeaponProfile`: empunhadura e clips por tipo de arma (espada, arco, lança) | Arco não pode usar ataque de cajado (§11.2) | Médio |
| P1 | Ranged: `aim`, `shoot`, `throw` com evento de projétil | Combate à distância inteiro está MISSING | Médio |
| P2 | `stunned` (laço), `respawn` (ação de entrada) | Estados de combate comuns em MMORPG | Baixo |
| P2 | Variações de interação: `pickup` (abaixar), `talk`, `use_item` | Interações distintas no jogo | Baixo |
| P2 | Root motion vertical: `jump`, `fall`, `land` | Exige mudar o contrato `in_place` e o validador de contato | Alto |
| P3 | Combos com clips próprios (ataque 2 e 3) | Hoje o combo repete o mesmo clip | Médio |
| P3 | Integração com o movimento do jogo (Pindorama Engine): travar deslocamento por prioridade | Hoje é regra documentada | Médio |
