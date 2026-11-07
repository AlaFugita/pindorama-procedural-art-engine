# Auditoria final de aprovação: Aprendiz (personagem mestre)

**Data:** 2026-11-07. **Escopo:** pedido do usuário em 6 itens. **G9:** continua `REVIEW`. A decisão artística é do usuário.
Evidências em [master_audit/](master_audit/). O personagem não foi reconstruído: só recebeu correções pontuais, listadas abaixo.

## 1. Animações

Os GIFs reais mostram as oito direções na velocidade do jogo (fps do manifesto: idle 8, walk 12, run 16):

- [idle_8dir.gif](master_audit/animacoes/idle_8dir.gif)
- [walk_8dir.gif](master_audit/animacoes/walk_8dir.gif)
- [run_8dir.gif](master_audit/animacoes/run_8dir.gif)

Há também a versão **no mundo**, em que o sprite anda à velocidade do clip sobre marcas fixas no chão:

- [walk_8dir_mundo.gif](master_audit/animacoes/walk_8dir_mundo.gif)
- [run_8dir_mundo.gif](master_audit/animacoes/run_8dir_mundo.gif)

E as folhas quadro a quadro, com a linha do chão no pivô: [walk_quadros.png](master_audit/animacoes/walk_quadros.png), [run_quadros.png](master_audit/animacoes/run_quadros.png) e [idle_quadros.png](master_audit/animacoes/idle_quadros.png).

Além do olho, usei uma sonda nova, `stage_audit_pose`. Ela mede a malha deformada em todos os quadros: o ponto mais baixo de cada peça e quanto da coxa sai da túnica, pela seção real do tecido.

| Item | Antes da auditoria | Depois das correções | Como |
|---|---|---|---|
| Alternância das pernas | Correta | Correta | Folhas quadro a quadro |
| Pés no chão | Botas a −2,3 mm em todos os clips | +0,7 mm | Sonda; sola subiu 3 mm |
| Deslizamento | 0,00002 H/s (walk) | 0,00006 H/s (run) | ANI-003 e GIF no mundo |
| Coxa × túnica | walk 10 mm; run 30,5 mm, visível na frente | walk 5,7 mm atrás; run 11,4 mm atrás e 6,3 mm na frente, invisível nas vistas S e SE | Sonda + zoom |
| Continuidade do ciclo | Laço fecha (ANI-004 = 0) | Igual | ANI-004 e folhas com o quadro 0 repetido |
| Cajado | Na corrida inclinava ~45° e afundava 2,4 cm no chão | Quase de pé; +0,6 mm do chão | Antebraço compensa o balanço do braço |
| Capuz e acessórios | Coerentes nas 8 direções | Iguais | Folhas |

Correções aplicadas, todas pontuais:

- **Sola das botas:** subiu 3 mm.
- **Cajado:** passou a nascer 2,5 cm mais alto.
- **Túnica:** a barra abriu de 1,3 a 1,5 cm.
- **Coxas:** afinaram, ficando ocultas sob a túnica.
- **Corrida:** passada de 0,22 para 0,19 m e erguida do pé de 6 para 4,5 cm.
- **Mão da arma:** o antebraço compensa o balanço do braço. Isso vale para qualquer personagem com arma.

**Resíduo conhecido:** a coxa sai 11 mm atrás no quadro 4 da corrida e 6 mm na frente no quadro 7. Não vi o efeito nas vistas frontais. A G6 segue em WARN porque o idle tem 3 quadros repetidos: o movimento é pequeno demais para 128 px.

## 2. Oito direções

[oito_direcoes_idle.png](master_audit/oito_direcoes_idle.png) e [oito_direcoes_walk.png](master_audit/oito_direcoes_walk.png) seguem o mesmo padrão: quadro original 128×128 sem recorte, com mesma escala, enquadramento e fundo. Cada direção tem rótulo e ângulo, a cruz do pivô e uma faixa embaixo em tamanho real.

O cajado fica na mão esquerda e a bolsa no quadril direito em todas as direções. O bico do capuz aparece nas vistas de lado e de costas.

Defeito visível: a borda creme do capuz chega à silhueta sem contorno escuro em NE e NW, como faixa clara.

## 3. Transparência, nos 216 PNG originais

O teste roda sobre os 192 quadros e os 24 atlases: [transparencia.json](master_audit/transparencia/transparencia.json). A prova sobre preto, branco e magenta está em [transparencia_fundos.png](master_audit/transparencia/transparencia_fundos.png).

| Verificação | Render suave (mestre) | Pixel art |
|---|---|---|
| Modo RGBA com canal alpha | 216/216 | 216/216 |
| Fundo embutido (borda ou magenta opaco) | 0 | 0 |
| Semitransparente no miolo | 12 px | 0 |
| Franja clara na borda, sem contorno | 2.060 px, em 128 arquivos | 0 |
| Cor guardada em pixel invisível (> 2/255) | 21.612 px | 0 |
| Pixels semitransparentes | 187.262 (antialiasing) | 0 |

O render suave não embute fundo. Ele tem, porém, franja clara onde a borda creme do capuz chega à silhueta sem contorno, além de resíduos de cor em pixels invisíveis. O "Fix Alpha Border" do Godot trata esse resíduo. O pixel art passa em tudo, porque o alpha é binário por construção.

## 4. Personalização modular

São cinco fichas, e cada uma difere do Aprendiz em **um único campo**. As cinco passaram no pipeline completo, até o Godot.

A comparação usa o hash da malha de cada peça, gerado no build ([modular.json](master_audit/modular/modular.json)). A folha visual está em [variacoes.png](master_audit/modular/variacoes.png).

| Variação | Campo da ficha | Peças iguais ao base | O que mudou |
|---|---|---|---|
| Cor do capuz | `palette.primary` | 26 de 26 | Só a cor do material |
| Cabelo | `appearance.hair_asset` | 25 de 26 | `hair` |
| Roupa | `outfit.body_asset` | 22 de 24 | Sem capuz e capa; com colete e gola |
| Acessório | `outfit.accessories` | 24 de 26 | Bolsa trocada por grimório |
| Arma | `outfit.weapon_asset` | 25 de 27 | Cajado reto, com `staff_gem` |

Rig, animação e perfil de render são idênticos nas cinco.

Para trocar, basta editar um campo da ficha: nada é modelado de novo. O pipeline, porém, refaz o build da cena (1,4 s) e renderiza de novo as 192 imagens (~27 s), porque os pixels mudam. Não existe cache de render por peça.

Limites:
- A roupa sem capuz mostra o cabelo como um capacete liso, porque a cabeça foi pensada para ficar sob o capuz.
- O cristal da arma ficava escondido atrás do capuz. O cajado de cristal foi alongado, a variação foi renderizada de novo, e o cristal agora aparece nas quatro vistas.

## 5. Suave × pixel art

Mesmo modelo nos dois. Comparação em tamanho real: linhas 1 e 2 de [antes_depois.png](detalhamento/antes_depois.png). O pixel art usa o perfil `pindorama_pixel_art_detailed_v1`, documentado em [DETALHAMENTO_ARTISTICO.md](../DETALHAMENTO_ARTISTICO.md). Nenhum estilo foi fixado para o MMORPG.

## 6. Prestação de contas

Atualizei STATUS, DECISIONS, VALIDATION_REPORT, RESEARCH_LOG e o Kanban. Nenhuma família nova foi criada, e o G9 não foi aprovado.
