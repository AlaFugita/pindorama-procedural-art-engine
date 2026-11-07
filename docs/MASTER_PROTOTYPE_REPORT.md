# Character Master Prototype — relatório

**Data:** 2026-11-07  
**Estado:** **duas rotas produzidas em quatro vistas de argila. Nenhuma aprovada; a decisão é humana (regra 3).**  
Tentativas de referência: Rota A `t08`, Rota B `t03`. Evidências em `docs/audit/master_prototype/`.

| Evidência | Arquivo |
|---|---|
| Quatro vistas, A × B | `comparativo_quatro_vistas.png` |
| Rosto, A × B | `comparativo_rosto.png` |
| Escala de jogo, A × B | `comparativo_escala_jogo.png` |
| Lado a lado com a referência | `rota_a_lado_a_lado.png`, `rota_b_lado_a_lado.png` |
| Pose extrema | `rota_a_pose_extrema.png`, `rota_b_pose_extrema.png` |

## Veredito do agente

Avaliação, não aprovação.

| Pergunta | Melhor rota |
|---|---|
| Quem chega mais perto da identidade? | **B**, com folga: rosto, punhos, abdômen, colar, tanga, postura |
| Quem tem a estrutura de produção? | **A**: quads, UV no corpo, peças separadas, proporção certa |
| Alguma serve sozinha? | **Não** |

**As rotas falham em lados opostos e por isso são complementares.** A Rota B tem a arte e não tem a estrutura. A Rota A tem a estrutura e não tem a arte na cabeça. A Rota C, testada a seguir, une parte das duas e também não é aprovável.

## Comparação objetiva

| Critério | Rota A (t08) | Rota B (t03) | Vantagem |
|---|---|---|---|
| Silhueta | IoU 0,57 em 3/4; clara a 30° | IoU 0,81 em 3/4; ver ressalva | B |
| Proporções | **3,51 cabeças**, atende D2 | **~4,5 cabeças, não atende D2**; herda o herói | A |
| Rosto | Sem pálpebra, adulto, sem identidade | Jovem e estruturado; olhos rasos, sem sobrancelha pesada | **B** |
| Volumes | Bons no corpo; cabelo fraco | Ricos e orgânicos na frente; superfície derretida nos detalhes | B |
| Anatomia | Boa; mãos abertas | Boa de frente: punhos, peito, abdômen, joelhos; pés fundidos ao calçado | B |
| Qualidade da geometria | 76.730 faces, 98,8% quads; corpo fechado; 30 peças | 962.762 triângulos, 0 quads, 42 componentes, ruído fino | **A** |
| Personalização | 30 peças, troca direta | Malha fundida: pele, roupa e cabelo não separam | **A** |
| Rigging | p99 1,60×, pico 15,6×; ombreira solta | p99 5,32×, pico 48,5×; saia rasga com as pernas | **A** |
| Custo computacional | ~5 s de CPU, sem VRAM | 143 s, 4,7 GB de VRAM, 7,4 GiB de pesos, 4,9 GB de ambiente | A |
| Licenciamento | CC0 + código próprio | Código e pesos MIT; ver pendências | A |

**Polígonos não contam como mérito:** a B tem 12× mais faces, e isso é passivo de produção, não qualidade.

### Ressalvas das medidas

- **O IoU favorece a B por construção:** ela foi gerada a partir da mesma imagem medida. A vista 3/4 é a que o modelo viu. Costas e perfil não têm referência equivalente.
- O teste de rig usa esqueleto simples, sem IK nem ajuste de pesos. Na B, as articulações foram lidas por olho na vista frontal e a malha foi decimada a 20%, o que pode piorar o número.
- A proporção da B vem do perfil da malha, com leitura manual do queixo: é estimativa. O valor automático do script (2,26) usa critério da Rota A e é inválido para a B.

## Defeitos específicos da Rota B

| Defeito | Causa provável | Corrigível? |
|---|---|---|
| Placa plana atrás da cabeça | Bordas retas da máscara do agente que removeu arco e aljava (hipótese) | Sim, com entrada melhor |
| Forma tipo rosto nas costas | Invenção do modelo: a vista não existe na entrada | Exige limpeza |
| Lâminas retas nos ombros | Mesma origem da placa (hipótese) | Sim, com entrada melhor |
| Superfície derretida em faixas e sandálias | Limite do modelo | Parcial |
| Dedos dos pés ilegíveis, sem sandália real | Limite do modelo | Exige escultura ou troca de peça |

## Histórico de execução da Rota B

Tudo foi executado localmente pelo usuário. Nada foi enviado para fora.

| Tentativa | Resultado |
|---|---|
| 1ª | Falhou ao carregar: script não importava módulos do TripoSG |
| 2ª (`t01`) | Inválida: casca falsa e degraus, por preenchimento NaN do agente |
| 3ª (`t02`) | Inválida: extração corrigida, mas 30,4% das faces alinhadas à grade |
| 4ª (`t03`) | **Válida:** decodificador float32 + caminho hierárquico, 0,8% alinhadas |

A mudança simultânea de precisão e de caminho não isola a causa: a variante rápida em float32 falhou por conflito de dtype. Só se sabe que a combinação funciona.

## Tecnologia da Rota B

TripoSG, commit `fc5c409`; pesos `VAST-AI/TripoSG`, commit `2c1c516`, MIT, safetensors. Usa Python 3.12, torch 2.11 e diffusers 0.42, diferentes do que o projeto indica. RMBG-1.4 (não comercial) não foi usado; a máscara é própria.

**Pendências de licença antes de qualquer uso em produção (regra 4):**
- revisar as dependências do ambiente e a origem dos dados de treino;
- avaliar a proteção autoral de saídas geradas a partir de imagem de IA (ver `REFERENCE_PROVENANCE.md`).

## Rota C — resultado (t05)

Forma da B sobre a estrutura da A: B levada a 3,5 cabeças, topologia da base projetada no rosto, cabelo e penas da B recortados como peça. Usou a malha B `t03`, sem nova execução do TripoSG. Código: `blender/scripts/ics_blender/stage_master_c.py`. Evidências: `comparativo_abc_quatro_vistas.png`, `comparativo_abc_rosto.png`, `rota_c_lado_a_lado.png`, `rota_c_pose_extrema.png`.

**Avaliação do agente:** a hipótese central foi confirmada só em parte. A identidade do cabelo e a proporção sobrevivem à estrutura da A. **O rosto perde leitura e o acabamento não é aprovável.**

| Critério | Rota C (t05) | Comparação |
|---|---|---|
| Silhueta | IoU 0,61 em 3/4; lê bem na câmera de jogo | Acima da A (0,57) |
| Proporções | **3,51 cabeças medidas**, atende D2 | Igual à A |
| Rosto | Quads limpos e mais jovem que a A; olhos fechados, boca aberta, sem a força da B | Entre A e B |
| Volumes | Cabelo da B com massa e direção; corpo da A | Melhor combinação |
| Anatomia | Corpo da A; mãos abertas, sem os punhos da referência | Igual à A |
| Geometria | 100.272 faces: 59.760 quads (corpo 100%) e 40.468 tris (cabelo) | Pior que A, muito melhor que B |
| Personalização | 24 peças; cabelo separado do corpo | Próxima da A |
| Rigging | p99 1,52×, pico 6,8×; ombreira ainda solta | **Melhor das três** |
| Custo | Geração da B + montagem em CPU | Acima da A |
| Licença | CC0 + código próprio + saída do TripoSG (pendências da B) | Como a B |

### Defeitos abertos da Rota C

| Defeito | Causa | Estado |
|---|---|---|
| Corte visível entre cabeça e pescoço | Recorte reto do cabelo em z = 0,93 e transição da máscara | Aberto |
| Boca aberta | Cavidade da base; raios frontais não resolveram | Aberto |
| Placa, nuca e laterais sujas | Entrada da B e recorte | Aberto; entrada nova deve ajudar |
| Olhos sem definição | Sem globos; a B tem órbitas rasas | Aberto |
| Mechas e penas sem UV, com 1 peça em triângulos | Saída da B | Exige retopologia |
| Dobras finas no rosto | Interior da base dobrado na projeção | Reduzido, não eliminado |

### Histórico da Rota C

| Tentativa | Mudança | Resultado |
|---|---|---|
| t01 | Projeção direta | Identidade aparece; dobras e furos no cabelo |
| t02 | Relaxar e projetar | Rosto limpo; pele colou no cabelo |
| t03 | Máscara até a sobrancelha | **Melhor rosto**, mas 3,62 cabeças |
| t04 | Raios frontais + base de cabelo da A | **Regressão**, revertida |
| t05 | Queixo corrigido | 3,51 cabeças; rosto perde parte da leitura de t03 |

### Resposta à regra 8

A escultura humana especializada **ainda não é obrigatória, mas é a rota provável para a cabeça final**. A automação transferiu proporção e cabelo, porém cada ajuste de cabeça passou a trocar um defeito por outro. Resta um passo barato e de alto impacto: refazer a entrada da B. Se ela não limpar nuca e cabelo, o acabamento da cabeça deve ir para uma pessoa, usando a Rota C como bloco de partida.

## Entrada refeita (Rota B t04, Rota C t06)

**Status atual do protótipo.** As tabelas acima de t03/t05 ficam como histórico. Evidências atuais: `comparativo_abc_quatro_vistas.png`, `comparativo_abc_rosto.png`, `rota_c_lado_a_lado.png`.

A máscara foi retraçada: a pluma é protegida por contorno, e arco e aljava saem seguindo a borda do corpo. **A hipótese foi confirmada:** placa, aba e forma nas costas desapareceram na malha nova. Boca fechada, orelhas, costas e ombreira também melhoraram na Rota B.

| Critério | Rota B t04 | Rota C t06 |
|---|---|---|
| Proporções | ~4,4 cabeças (estimativa) | **3,49 cabeças medidas** |
| Silhueta (IoU 3/4) | 0,81 | 0,57 |
| Geometria | 992.918 triângulos, 52 componentes | 100.272 faces; corpo em quads; cabelo em triângulos |
| Rigging (p99 / pico) | 5,04× / 57,1× | 1,52× / 6,8× |
| Peças | Malha fundida | 24 peças |

O IoU da C caiu de 0,61 para 0,57 porque a pluma ficou maior que a da referência. É um defeito real, mas a medida não capta o ganho de rosto e cabelo.

**Avaliação do agente:** a Rota C t06 é a primeira versão com identidade forte sobre a estrutura correta. Ainda não é aprovável.

### Defeitos abertos da Rota C t06

| Defeito | Causa provável |
|---|---|
| Boca aberta | Cavidade da base; sem solução automática até aqui |
| Corte e sobras de cabelo no pescoço | Recorte reto e faixa mantida atrás do pescoço |
| Pluma em forma de bolsa, exagerada | Modelo gerou volume onde a imagem só mostrava silhueta |
| Dobras e manchas nos olhos | Órbitas rasas da B e interior da base |
| Mãos abertas, colar e ombreira menos fiéis | Peças ainda da Rota A; a B tem versões melhores |
| Cabelo sem UV, em triângulos | Saída da B: exige retopologia |

### Resposta atualizada à regra 8

Forma e identidade por automação estão demonstradas. O **acabamento** da cabeça (boca, olhos, pescoço, retopologia do cabelo) é o trecho que provavelmente exige mão humana. Fica como decisão do usuário, depois de revisar `G3M`.

## Candidato atual: Rota C t09

**Versão candidata à revisão humana no G3M.** Sem aprovação. Evidências: `comparativo_abc_quatro_vistas.png`, `comparativo_abc_rosto.png`, `rota_c_quatro_vistas.png`, `rota_c_rosto.png`, `rota_c_lado_a_lado.png`, `rota_c_pose_extrema.png`.

| Tentativa | Mudança | Resultado |
|---|---|---|
| t07 | Punhos e colar recortados da B | **Falhou:** punhos em lascas, colar com retângulo de pele. Revertido: a pele da B não se separa do que está fundido a ela |
| t08 | Remendo da boca com a superfície da B | **Boca fechada**, com expressão firme |
| t09 | Máscara termina no queixo; sobras do pescoço removidas | Anel do pescoço quase eliminado; cabeça ligada ao corpo |

Causa real da boca: o interior da base achatava sobre a superfície com faces invertidas. A hipótese anterior do agente, de pele da B dentro do cabelo, estava errada para a boca, embora valesse para as manchas junto aos olhos.

| Medida (t09) | Valor |
|---|---|
| Proporção | 3,49 cabeças medidas |
| Rigging | p99 1,51×, pico 6,8× |
| Peças | 25 objetos |

### Defeitos abertos

| Defeito | Natureza |
|---|---|
| Pluma exagerada e recortada | Forma; exige decisão artística ou escultura |
| Mechas laterais e fundo do cabelo com corte reto | Recorte |
| Olhos fechados, com dobras finas | Forma; olhos podem vir de pintura, a validar |
| Traços leves da caixa do remendo no rosto | Costura |
| Mãos abertas; colar, ombreira e tronco da Rota A | Peças; transplante por recorte não funciona |
| Cabelo sem UV, em triângulos | Exige retopologia |
| Ombreira solta na pose extrema | Pesos |

### Ponto de parada

A partir daqui, cada ajuste depende de julgamento artístico. Pela regra 3, a próxima decisão é humana: revisar a t09 no G3M. Textura e animação seguem bloqueadas até lá (regras 1 e 2).

## Aprovação como base e teste de textura

**G3M:** o usuário aprovou a Rota C t09 **somente como forma base**, em 2026-11-07, não como arte final. Arquivo preservado em `library/masters/guardiao_t09/master_c.blend`, sha256 `81d766b8fc2fdc4e27dd776d2c3541e9f0bd30488f365f727878acee735a6bbb`. G9 permanece `REJECTED`.

**Teste de direção de textura (`paint/t03`), local.** Evidências: `textura_quatro_vistas.png`, `textura_quatro_vistas_jogo.png`, `textura_rosto_34.png`, `textura_lado_a_lado.png`, `textura_escala_jogo.png`.

| Tentativa | Método | Resultado |
|---|---|---|
| t01 | Projeção da prancha em tudo | Colcha de retalhos: pose da B difere da prancha; cores lavadas por erro de espaço de cor |
| t02 | Projeção só na cabeça + cor por peça | Corpo funcionou; rosto pintado de lado (ajuste por silhueta errou o ângulo) |
| t03 | Setor do ângulo restrito à frente | **Rosto, cabelo e penas com a identidade da referência** |

| Medida | Referência | Pintado (t03) | Personagem reprovado |
|---|---|---|---|
| Detalhe (apresentação) | 0,0405 | 0,0185 | 0,0132 |
| Cores (5 bits) | 2.814 | 1.831 | 559 |
| Sombra (luma p5) | 0,075 | 0,100 | 0,18 |
| Detalhe (sprite) | 0,0265 | 0,0232 | 0,0215 |

**Avaliação do agente:** a cabeça fecha a distância nas duas escalas. O corpo, em cor chapada, é agora o que mais se afasta: faltam músculos pintados, grafismos, desgaste e sombra. A hipótese de que a pintura carrega a arte foi confirmada para a cabeça.

**Limites do teste:**
- É cor por vértice, não textura em UV: detalhe limitado à densidade da malha, com facetas visíveis de perto.
- Rosto e cabelo só foram vistos pela prancha em um ângulo. Perfil e costas da cabeça são estimados e mais fracos.
- Sprite e herói da referência diferem: a comparação em jogo usa o sprite da prancha, que não é o mesmo recorte do render.
- Pintura esconde defeitos de forma (regra 2): olhos fechados, por exemplo, só parecem abertos por estarem pintados. Isso é aceitável para olhos estilizados, mas precisa ser decisão humana.
- A projeção usa a imagem local: nada saiu da máquina (D4).

## Sonda de risco: um sprite pintado (t09, p02)

Exceção à regra 2 autorizada pelo usuário em 2026-11-07, só para medir risco. Não aprova nada e não é etapa de produção. Pintura simples por vértice, com a paleta da prancha, na câmera do jogo. Evidências: `sonda_sprite_p02.png`, `sonda_apresentacao_p02.png`. Código: `stage_master_paint.py`, `scripts/master_paint_test.py`.

**Resultado da sonda: longe da referência, mas a sonda é mais fraca que o teste `paint/t03`.** Foi executada sem conhecer a aprovação da base e o teste de textura registrados acima, feitos em outra sessão. Ela pinta a cabeça por região; `paint/t03` projeta a prancha e obtém rosto e cabelo com identidade.

| Medida no sprite | Referência | Mestre pintado |
|---|---|---|
| Sombra (luminância p5) | 0,077 | 0,054 |
| Luz (luminância p95) | 0,55 | 0,57 |
| Detalhe | 0,0739 | 0,0523 |
| Cores (5 bits) | 1.211 | 466 |

Faixa de valores e paleta chegaram perto. Detalhe e cores não, e as medidas não captam o principal, que é a leitura visual.

| Causa da distância | Natureza |
|---|---|
| Rosto pouco legível com pintura por região | Da sonda: `paint/t03` resolve por projeção |
| Massa de cabelo e pluma domina a silhueta | **Estrutural**, ainda visível em `paint/t03` |
| Tronco e roupa da Rota A, mais simples que os da referência | **Estrutural** |
| Tanga e peças sem camadas nem desenho | Pintura simples + forma |
| Sem pintura de luz, desgaste e grafismos | Pintura simples |

Conclusão válida somada a `paint/t03`: a cabeça projetada funciona, e o corpo é a maior distância restante. A sonda não justifica trocar de caminho.

## Pintura do corpo (`paint/t05`)

Local, sem IA e sem imagem de terceiros. Módulo: `blender/scripts/ics_blender/body_paint.py`. Evidências: `corpo_quatro_vistas.png`, `corpo_quatro_vistas_jogo.png`, `corpo_escala_jogo.png`, `corpo_lado_a_lado.png`.

Mantém a cabeça projetada de `paint/t03` e pinta o corpo com volumes, sombras e grafismos, com contorno escuro. A luz pintada usa só inclinação vertical e curvatura, então vale em todas as direções, sem exigir pintura por vista.

| Medida | Referência | t03 | t05 |
|---|---|---|---|
| Detalhe (apresentação) | 0,0405 | 0,0185 | 0,0265 |
| Sombra (luma p5) | 0,075 | 0,100 | 0,074 |
| Luz (luma p95) | 0,68 | 0,821 | 0,638 |
| Detalhe (sprite) | 0,0265 | 0,0232 | 0,0261 |

**Avaliação do agente:** primeira versão que se lê como personagem de jogo nas quatro vistas, com cabeça e corpo no mesmo estilo. Ainda não iguala a referência. Métricas são indicadores, e a decisão é humana.

Pendências:

- penas do ombro continuam laranja, deveriam ser vermelhas;
- roupa da Rota A: sem cinto largo, pouco volume, tanga mais simples que a referência;
- músculos e desgaste ainda sutis;
- verso do cabelo com manchas estimadas; pluma domina a silhueta;
- braçadeiras em padrão fino, que vira ruído no sprite;
- mãos abertas e olhos pintados sobre pálpebra fechada, o que precisa de decisão humana;
- cor por vértice, sem UV: não serve como textura final;
- não testado em animação, oito direções completas ou segundo personagem.

## Limitações gerais

- Nenhum dos dois personagens tem textura, por regra.
- Seed único na Rota B: outras sementes não foram testadas.
- MST-F1 (rig semântico completo) não foi executado em nenhuma rota.
- A Rota A tem hairline calibrada antes do último ajuste de escala da cabeça.
