# Decisões da pesquisa e próximos passos

**Importante:** o que está aqui é **recomendação de pesquisa**. As únicas decisões de implementação aprovadas estão em [../DECISIONS.md](../DECISIONS.md).

## Técnicas recomendadas

1. **Rim light e oclusão mais forte** no acabamento suave, logo após esta pesquisa.
2. **Textura discreta contínua** por grafo de nós (F2).
3. **`seed` na ficha** e detalhe pela resolução (F1).
4. **Curva com conicidade e torção** para mechas, cordões e, no futuro, galhos (F4).
5. **Atlas recortado.**

## Técnicas descartadas

- Síntese de textura por exemplo (texture-synthesis): arquivada e foge da geração por código.
- Personagem desenhado por direção em 2D (2d_chars): perde a consistência garantida pela fonte 3D.
- Copiar código do seedbank: não tem licença.

## Precisam de experimento

| Experimento | Problema | Esperado | Avaliação | Beneficia |
|---|---|---|---|---|
| E1. Rim + oclusão no `smooth.py` | Volume pouco legível no capuz | Borda clara no lado da luz e dobras mais escuras | Antes e depois na mesma vista, em tamanho real | Todos os assets suaves |
| E2. Ruído de baixa frequência no tecido | Áreas grandes "de plástico" | Variação de tom suave e estável entre quadros | GIF de caminhada sem piscar | Tecido, couro, pedra |
| E3. Midori CLI → GLB → render | Vegetação sem modelar | Árvore no mesmo acabamento suave | Folha de 1 a 4 vistas | Nature Generator |
| E4. `.gdshader` de tingimento | Variar cor em runtime | Mesma folha de sprite com 3 cores | Godot headless | Personagens, objetos |

## Repositórios a acompanhar

infinigen (arquitetura), midori (vegetação), Material Maker (materiais e Godot), texture-genetics (evolução de materiais).

## Sugestões ao roadmap

Antes da etapa 3 do roadmap: E1, E2 e o atlas recortado. Na etapa 7: E3. Na integração com engines: E4.

## Pendências de decisão (usuário)

- Aprovar o acabamento suave como principal: G9 e VIS-005.
- Resolução de referência: proposta de 192.
- Se usar o midori como ferramenta externa quando chegar a natureza.
