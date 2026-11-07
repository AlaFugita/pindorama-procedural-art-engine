# Arte gerada no ChatGPT (2026-11-07)

Retorno à rota canônica (`GERAR-ARTE-NO-CHATGPT.md`): o motor 3D procedural não alcançou o nível do Duende e do Saci.

- `gerado/indigena_5vistas_t1_opc1.png` e `_opc2.png`: protagonista indígena (pedido do usuário: substitui o mago), 5 vistas, fundo magenta. **Opção 1 aprovada pelo usuário em 2026-11-07** como personagem mestre (`mestre/protagonista_5vistas.png`).
- `gerado/mockup_vila_t2_indigena.png`: tela-alvo de clima e estilo. Não é planta técnica: ângulo, escala de tile e distâncias serão fixados pela engine.
- `gerado/mago_detalhe_5vistas_t1.png` e `mockup_vila_t1_mago.png`: rodada anterior com o Mago, já fora de foco.
- `antes_depois_2026-11-07.jpg`: comparação com o motor 3D.
- `refs/`: referências do próprio Pindorama anexadas ao ChatGPT.

Restrições do desenho: sem cocar, penas, pintura corporal, grafismos ou símbolos cerimoniais reais (regra 10 de `GERAR-ARTE-NO-CHATGPT.md`; elemento cultural real exige dossiê).
Lição registrada: L-013 em `ponte/LICOES-DE-ARTE.md`.

## Folhas preparadas (`prep/`)
- `protagonista_andar_E.png`: tira 1024×128 (8 quadros de 128 px, fundo transparente), da folha `gerado/indigena_andar_E_t1.png` (1ª tentativa, prompt da L-009). Prévia: `_previa.gif`; contato: `_contato.png`.
- `protagonista_parado_<S|SE|E|NE|N>.png`: parado nas 5 direções, do mestre.
- Preparo: `preparar_liso.py` do PR-08 (escala única, pé no pixel 124, sem paleta reduzida).
- Observação: a 128 px o contorno escuro fica fino; pode ser engrossado no preparo se o jogo pedir.

## QA e correções por código (o ChatGPT sempre deixa errinhos)
- `qa_sprites.py`: mede por quadro a altura, a linha do pé, a tremida da cabeça e a cor de pele, túnica e cabelo contra o mestre. Antes da correção: pé fixo em 124 ✅, tremida da cabeça < 1 px ✅, altura 104–111 px (balanço do passo), túnica de E e SE ~10% mais escura (Δ 26) ❌.
- `normaliza_cores.py`: ganho por material, igual para os 8 quadros de cada tira. Depois: túnica Δ ≤ 17 e pele Δ ≤ 9. Os originais ficam em `*_bruto.png`.
- `contorno.py`: devolve 1 px de contorno marrom-escuro que some na redução para 128 px. Os arquivos sem contorno ficam em `*_semcontorno.png`.
- Revisão visual das 40 poses (`prep/protagonista_andar_prancha_qa.png`): sem dedos extras, sem alça trocada, sem peça sumindo.
- **Decisão de convenção:** o ChatGPT põe o cajado sempre à direita da tela. Isso significa a mão esquerda nas vistas de frente e a direita nas de costas. Na tela fica consistente (não pula ao girar). Como o oeste é o espelho do leste, a mão "física" se perderia de qualquer jeito. Fica a regra "cajado à direita da tela no lado leste".
- Prévia final: `prep/protagonista_andar_8direcoes.gif` (W, SW e NW espelhados).
