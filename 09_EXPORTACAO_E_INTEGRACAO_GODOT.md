# 09 — Exportação e integração com Godot

## 1. Objetivo

Entregar arquivos simples, documentados e previsíveis para que o projeto Godot consuma personagens sem depender do aplicativo gerador durante a execução do jogo.

## 2. Formatos

| Formato | Uso |
|---|---|
| PNG RGBA | Frames e spritesheets com transparência |
| JSON | Dados do personagem, animações, frames e manifests |
| GLB | Intercâmbio de modelo 3D, quando aplicável |
| BLEND | Fonte editável do Blender; não é formato de runtime Godot |

## 3. Estrutura de exportação sugerida

```text
exports/
└── forest_guardian/
    ├── character.json
    ├── manifest.json
    ├── source/
    │   ├── character.blend
    │   └── character.glb
    ├── animations/
    │   ├── idle/
    │   ├── walk/
    │   └── run/
    ├── atlases/
    │   ├── idle_N.png
    │   ├── idle_NE.png
    │   ├── walk_N.png
    │   └── run_N.png
    └── metadata/
        ├── animations.json
        └── directions.json
```

A estrutura poderá ser ajustada durante a integração, mas não deve mudar sem atualizar o schema e os testes.

## 4. Metadados de animação — exemplo

```json
{
  "schema_version": "1.0.0",
  "character_id": "character_001",
  "animation": "walk",
  "fps": 12,
  "loop": true,
  "direction_order": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
  "directions": {
    "S": {
      "file": "../../atlases/walk_S.png",
      "frame_width": 128,
      "frame_height": 160,
      "frame_count": 8,
      "pivot": {"x": 64, "y": 150}
    }
  }
}
```

O exemplo mostra uma direção e valores ilustrativos. O arquivo real deve conter todas as direções e os retângulos/índices efetivos dos frames.

## 5. Atlas: por direção ou consolidado?

Recomendação inicial: um atlas por animação e direção, ou uma sequência PNG por direção quando isso simplificar a importação. Evitar um atlas único gigantesco no MVP.

A decisão final deve considerar:

- número de frames;
- limites de textura da plataforma alvo;
- carregamento seletivo;
- tamanho de arquivo;
- facilidade de depuração;
- ferramenta de importação do Godot.

## 6. Godot Export Bridge

O Bridge poderá gerar uma estrutura Godot contendo:

- texturas;
- dados de frames;
- recurso `SpriteFrames`;
- cena demonstrativa com `AnimatedSprite2D`;
- script auxiliar para selecionar direção;
- dados do personagem.

O gerador deve usar APIs e recursos realmente disponíveis na versão do Godot escolhida e ser testado com um projeto mínimo versionado.

## 7. Seleção de direção

O Godot recebe a direção de gameplay, converte para a convenção canônica e escolhe o clip correspondente.

Exemplo conceitual em GDScript:

```gdscript
const DIRECTION_NAMES := ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

func play_directional_animation(base_animation: String, direction_index: int) -> void:
    var index := posmod(direction_index, DIRECTION_NAMES.size())
    var direction_name := DIRECTION_NAMES[index]
    $AnimatedSprite2D.play(base_animation + "_" + direction_name)
```

O exemplo pressupõe que os recursos `SpriteFrames` foram criados com nomes como `walk_N`, `walk_NE` etc. O mapeamento de vetor para índice deverá ser implementado e testado no projeto de jogo, pois depende da convenção de coordenadas utilizada.

## 8. Validação de importação

Um projeto Godot de teste deverá comprovar:

- importação das texturas;
- transparência correta;
- reprodução de cada animação;
- seleção das oito direções;
- pivô e alinhamento estáveis;
- escala consistente;
- ausência de arquivos ausentes;
- compatibilidade com a versão-alvo do Godot.

## 9. Separação de responsabilidades

O Character Studio exporta visual e metadados. O MMORPG controla movimento, colisões, gameplay, sincronização de rede, estados de combate e lógica de entidades.
