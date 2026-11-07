# Recomendações técnicas priorizadas

**Prioridade:** P1 = próxima; P2 = depois do mestre aprovado; P3 = quando o domínio chegar.

## 1. Qualidade visual

| Pri. | Oportunidade | Benefício | Componente | Técnica | Complex. | Riscos | Recomendação |
|---|---|---|---|---|---|---|---|
| P1 | Textura discreta contínua | Tira o "liso de plástico" das áreas grandes (capuz, capa) | Passe de luz, papéis de material | Grafo de nós: ruído de baixa frequência + costura + desgaste (F2) | Média | Ruído piscar entre quadros: usar coordenadas do objeto, que já é o caso | **Adotar** |
| P1 | Luz de borda (rim) e oclusão mais forte nas dobras | Volume e profundidade no estilo suave | `smooth.py` | Rim pela distância à silhueta no lado da luz; oclusão com raio maior | Baixa | Exagero | **Adotar** |
| P1 | Mechas por curva com conicidade e torção | Cabelo mais orgânico | `chibi_detail`, `geometry.py` | Curva com raio (F4) | Baixa | — | **Adaptar** (conceito do midori) |
| P2 | Barras recortadas por SDF | Capa e capuz com ponta e rasgo | `geometry.py` | SDF 2D (F6) | Média | — | **Adaptar** |
| P2 | Detalhe pela resolução | 128 sem peças que viram ruído | Perfil + build | F1 | Baixa | — | **Adotar** |

## 2. Capacidade de geração

| Pri. | Oportunidade | Técnica | Complex. | Recomendação |
|---|---|---|---|---|
| P2 | Anatomia parametrizada | Proporções da ficha → posições do rig e das peças | Média | **Adotar** |
| P3 | Árvores e vegetação | Weber-Penn (midori como ferramenta externa ou adaptação) | Alta | **Estudar posteriormente** |
| P3 | Construções e ambientes | WFC, BSP, mistura de ruídos | Alta | **Estudar posteriormente** |
| — | Síntese por exemplo | texture-synthesis | — | **Descartar** (arquivado; foge da geração por código) |

## 3. Arquitetura

| Pri. | Oportunidade | Técnica | Complex. | Recomendação |
|---|---|---|---|---|
| P1 | `seed` explícita na ficha | F1 | Baixa | **Adotar** |
| P2 | Máscara de material + shader de tingimento no Godot | F3 | Média | **Adotar** |
| P2 | Catálogo de assets gerados com auditoria | F11 | Baixa | **Adotar** |

## 4. Desempenho

| Pri. | Oportunidade | Técnica | Complex. | Recomendação |
|---|---|---|---|---|
| P1 | Atlas recortado | Caixa justa por quadro + offset no manifesto | Média | **Adotar** (veja `DETALHAMENTO_ARTISTICO.md` §5) |
| P2 | Orçamento de geração | Estimar peças e triângulos antes do build (F4) | Baixa | **Adotar** |
| P2 | Passes em paralelo | Vários Blenders por direção | Média | **Estudar** (memória da GPU) |

## 5. Produtividade e manutenção

| Pri. | Oportunidade | Técnica | Recomendação |
|---|---|---|---|
| P1 | Levar as sondas de auditoria para os gates | `master_audit_*` → G5 e G6 | **Adotar** |
| P2 | Grafo de material declarativo (JSON) | Mini NodeWrangler | **Adotar** com F2 |
