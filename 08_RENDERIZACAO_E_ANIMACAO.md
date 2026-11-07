# 08 — Renderização, câmera e animação

## 1. Objetivo

Gerar sequências de quadros 2D a partir do mesmo personagem 3D, mantendo escala, enquadramento, luz, ponto de apoio e identidade visual nas oito direções.

## 2. Projeção e câmera

- Projeção ortográfica.
- Elevação e azimute configuráveis por `RenderProfile`.
- Uma convenção única de coordenadas entre Blender e Godot.
- Câmera e distância calibradas por família de personagem.
- Margens suficientes para armas, cabelos, asas e acessórios.

**Observação:** “isométrico” em jogos é frequentemente usado de forma ampla. O produto deve suportar uma câmera ortográfica com ângulos configuráveis; a escolha de uma projeção isométrica matemática estrita deve ser validada visualmente com o estilo do jogo.

## 3. Convenção das oito direções

Ordem canônica inicial, no sentido horário a partir do norte:

```text
0 = N
1 = NE
2 = E
3 = SE
4 = S
5 = SW
6 = W
7 = NW
```

A convenção deve ser mantida em:

- nomes de diretórios;
- metadados;
- atlas;
- seleção de direção no Godot;
- testes automatizados.

A orientação real de cada vista deverá ser calibrada com uma cena de teste. Não presumir que “N” do jogo corresponda automaticamente ao eixo Z positivo ou negativo do Blender.

## 4. Renderizar a câmera ou girar o personagem?

A solução recomendada é manter uma convenção única de orientação do personagem e gerar vistas por rotação controlada entre câmera e modelo.

A implementação deverá decidir uma estratégia principal após um teste comparativo:

- câmera orbitando o personagem;
- personagem girando diante de câmera fixa.

Ambas podem produzir resultados válidos; a decisão depende de sombra, iluminação, acessórios direcionais e convenção do gameplay. O que não deve ocorrer é misturar estratégias sem regra.

## 5. Animações iniciais

| Clip | Uso | Loop |
|---|---|---|
| `idle` | personagem parado | Sim |
| `walk` | caminhada | Sim |
| `run` | corrida | Sim |
| `emote` | gesto/expressão | Conforme clip |
| `cast` | habilidade | Conforme clip |
| `hit` | reação | Não, normalmente |
| `death` | estado de derrota | Não |

MVP: `idle`, `walk` e `run`.

## 6. FPS e quadros

Uma configuração inicial de teste pode usar 12 FPS e 8 quadros para ciclos simples, mas isso é um perfil de partida, não uma regra universal. FPS e número de quadros precisam ser configuráveis por animação.

O sistema deve distinguir:

- FPS de reprodução;
- número de frames;
- duração do clip;
- frames efetivamente renderizados;
- loop e transições.

## 7. Rigs

Cada família corporal deve declarar:

- hierarquia de ossos;
- nomes obrigatórios;
- convenção de orientação;
- escala de referência;
- pontos de ancoragem;
- clips compatíveis;
- validações de deformação.

Primeira família: humanoide padrão. Não assumir que um rig humanoide atende quadrúpedes, serpentes, dragões ou criaturas com anatomias diferentes.

## 8. Alinhamento e pivô

- Usar canvas de dimensão fixa por perfil/família.
- Definir pivô de personagem, preferencialmente no centro da base de apoio dos pés para humanoides.
- Garantir que o pivô permaneça no mesmo ponto lógico entre frames e direções.
- Não normalizar cada imagem isoladamente de forma que o personagem “pule” de tamanho.
- Não cortar acessórios que ultrapassem o volume corporal de referência.

## 9. Iluminação e sombras

A iluminação deve ser definida no perfil artístico. Se sombras projetadas forem necessárias no jogo, decidir se fazem parte da imagem ou se serão implementadas pelo motor de jogo. Não incluir sombras inconsistentes em alguns ângulos.

## 10. Nomenclatura de saída

Exemplo:

```text
walk/
  walk_N.png
  walk_NE.png
  walk_E.png
  walk_SE.png
  walk_S.png
  walk_SW.png
  walk_W.png
  walk_NW.png
```

Alternativamente, cada direção pode conter uma sequência de PNGs antes da montagem do atlas. O formato definitivo deve ser documentado no `ExportManifest`.
