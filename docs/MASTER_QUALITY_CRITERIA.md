# Critérios de qualidade do personagem mestre

Vigentes desde 2026-11-06. Complementam o doc 20 com o gate **G3M**, antes de G4 e G5.

## Regras de aprovação

1. Nenhuma animação avançada antes da aprovação do personagem mestre.
2. Nenhuma textura pode ocultar defeitos de geometria: a forma é avaliada em argila.
3. Nenhuma aprovação artística é automática. Métrica orienta; só pessoa aprova.
4. Nenhuma tecnologia entra sem análise de licença e compatibilidade.
5. Os testes existentes devem continuar aprovados.
6. A reprovação de G9 permanece no histórico; decisões anteriores nunca são apagadas.
7. Toda tentativa gera evidências visuais comparáveis, no mesmo estúdio.
8. Se nenhuma rota atingir o padrão artístico, apresentar a necessidade de escultura humana.

## Estúdio comparável

Mesmo para qualquer rota (`stage_master_clay`): Workbench, material neutro, sem textura e sem sombra projetada; ortográfica; frente, 3/4, perfil e costas a 0° e a 30°; closes de rosto. Altura de apresentação de 1200 px por vista.

## G3M — critérios

### A. Técnica (automática, bloqueante)

| ID | Critério | Limite |
|---|---|---|
| MST-T1 | Proporção medida | 3,5 ± 0,05 cabeças (`humanoid_35h_v1`) |
| MST-T2 | Corpo fechado e manifold | 0 aresta aberta, 0 não-manifold |
| MST-T3 | Corpo em quads | ≥ 98% |
| MST-T4 | Mesmo arquivo nas quatro vistas | Hash único |
| MST-T5 | Licença de todo asset e modelo | Registrada e permitida |

### B. Visual (humana, bloqueante)

Avaliar nas duas escalas, ao lado da referência.

| ID | Critério |
|---|---|
| MST-V1 | Silhueta reconhecível só em preto |
| MST-V2 | Rosto expressivo e legível |
| MST-V3 | Cabelo como massa desenhada, com direção |
| MST-V4 | Volumes e anatomia coerentes com a estilização |
| MST-V5 | Roupas com camadas distintas |
| MST-V6 | Identidade próxima da referência |
| MST-V7 | Consistência entre as quatro vistas |

Indicador auxiliar: IoU de silhueta em 3/4, a calibrar. Não aprova sozinho.

### C. Funcional (automática + revisão)

| ID | Critério |
|---|---|
| MST-F1 | Rig semântico aplicado, RIG-001 a RIG-004 aprovados |
| MST-F2 | Pose extrema sem NaN, sem peças soltas |
| MST-F3 | Alongamento de aresta p99 ≤ 1,5× (meta inicial, a calibrar) |
| MST-F4 | Peças removíveis para personalização |

Registro: `ics approve <personagem> G3M APPROVED|REJECTED --reviewer <nome>`.

## Fase de textura

Só depois de G3M aprovado em argila. A pintura deve ser avaliada de novo contra a mesma referência.
