# Análise do alvo visual: chibi do Mago

**Data:** 2026-11-07. **Contexto:** o usuário reprovou `paint/t05` e mandou decidir e refazer sem perguntar.

## O que estava errado

Construí uma figura de 3,5 cabeças a partir da prancha do ChatGPT sem ler a direção de arte do Pindorama. O alvo que o jogo já definiu é outro. Mais pintura não resolveria, porque o erro está na forma do personagem.

## O que os documentos dizem

| Fonte | Regra |
|---|---|
| `DIRECAO-DE-ARTE.md` | Chibi 2.5D, cabeça grande, formas redondas, contorno escuro grosso, olhos simples, cores chapadas com 2 a 3 tons de sombra, poucos detalhes |
| `ADR-0013` | Isométrico com sensação de Ragnarok Online |
| `mago_referencia_jogo.png` | Capuz azul com bico, borda creme, cabelo castanho, capinha, cinto, bolsa, cajado de ponta enrolada, botas |
| Medição nesta imagem | Capuz ocupa cerca de 44% da altura |

Ragnarok Online é o único jogo citado. Dele veio só a sensação: personagem pequeno, cabeça grande e leitura clara numa câmera alta. Nenhum asset dele foi copiado ou usado.

## Decisões tomadas

| Conflito | Decisão | Por quê |
|---|---|---|
| Prancha ou Mago | **Mago** | É a referência que o próprio jogo adotou |
| 3,5 cabeças (D2) ou chibi | **Chibi, cerca de 2,3 cabeças** | Exigência da direção de arte. Substitui D2 só neste caminho, com autorização delegada pelo usuário |
| Desenho liso ou pixel art | **Liso no render**, comparado ao Mago | A direção de arte pede desenho liso. O PNG do Mago é pixelado, então esse conflito segue aberto |
| 3D ou arte por código | **Mantém a cadeia 3D** para gerar sprites | Preserva oito direções, animação e Godot, já testados |

A prancha, a Rota C e `paint/t05` ficam preservadas como histórico. Nada foi apagado.

## O que foi construído

Personagem novo, feito por código, sem malha da Rota B ou C:

- `humanoid_chibi_v1`: rig de 33 ossos em altura de referência 1,0 m.
- `humanoid_chibi_basic_v1`: idle, walk e run para esse rig.
- `isometric_chibi_v1`: quadro de 128×128, medida da direção de arte.
- `pindorama_chibi_v1`: contorno quase preto, 3 tons e luz sem autossombra.
- Peças `chibi_*`, com o cajado na mão esquerda como no Mago.

## Limites

- A comparação com o Mago é visual e feita por mim. Só o usuário aprova arte.
- O Mago é pixel art e o nosso sprite é liso, então a fidelidade de traço não é medida por número.
- O rig chibi reutiliza a animação procedural; ninguém revisou o movimento a olho.
