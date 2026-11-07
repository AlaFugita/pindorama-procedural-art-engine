# 03 — Direção artística

## 1. Objetivo

Estabelecer uma linguagem visual uniforme para personagens humanoides, criaturas e NPCs do universo do MMORPG. O primeiro perfil será denominado `pindorama_stylized_v1`.

O nome é um identificador interno de perfil, não uma definição de que todos os personagens devam representar uma cultura específica.

## 2. Perfil visual inicial

| Propriedade | Diretriz |
|---|---|
| Categoria | Fantasy estilizado |
| Proporções | Chibi moderado, cabeça maior e corpo compacto |
| Formas | Silhuetas claras, volumes arredondados e leitura simples |
| Acabamento | Ilustração digital estilizada com aparência de asset de jogo |
| Contornos | Escuros, suaves e controlados; não necessariamente linha preta uniforme |
| Materiais | Leitura diferenciada para pele, tecido, couro, madeira, metal e pedra |
| Iluminação | Consistente entre personagens e direções |
| Sombras | Suaves e controladas, sem perder volume |
| Paleta | Saturação equilibrada, com cores de destaque limitadas |
| Texturas | Pintura estilizada; evitar aparência de pixel art no perfil inicial |

## 3. Regras de consistência

- Definir uma unidade de escala e uma altura de referência por família.
- Usar o mesmo perfil de câmera para personagens da mesma categoria de renderização.
- Fixar direção, intensidade e temperatura da luz principal.
- Padronizar materiais e resposta de superfície.
- Manter margens e ponto de apoio consistentes.
- Evitar detalhes que desapareçam na resolução final de gameplay.
- Avaliar o personagem na resolução de uso no jogo, não apenas em render ampliado.
- Preservar assimetrias intencionais, como acessórios em apenas um lado.

## 4. Referências culturais e autoria

Quando um personagem for inspirado em um povo, região ou tradição real:

1. identificar a referência cultural de forma específica;
2. pesquisar fontes confiáveis e, quando viável, consultar especialistas ou representantes;
3. não combinar símbolos, grafismos ou vestimentas de comunidades distintas sem justificativa;
4. distinguir fantasia original de representação cultural documental;
5. registrar referências e proveniência no projeto;
6. permitir revisão e remoção de elementos inadequados.

A expressão “indígena” não deve ser tratada como uma estética única ou universal.

## 5. Perfil artístico como dados

O perfil artístico deverá ser versionado e configurável, incluindo:

- proporções de referência;
- paletas autorizadas;
- materiais padrão;
- configurações de iluminação;
- parâmetros de câmera;
- regras de espessura visual/contorno, quando aplicável;
- resolução e escala de renderização;
- referências autorizadas e respectivas licenças.

## 6. Avaliação visual

Cada personagem deve ser avaliado em três escalas:

- **Close-up:** rosto, materiais, acessórios e acabamento.
- **Tamanho de gameplay:** silhueta e legibilidade.
- **Spritesheet:** continuidade entre direções e quadros.

A aprovação artística deverá considerar a leitura em movimento, não apenas uma imagem estática.

## 7. Critérios de rejeição

Rejeitar ou revisar um resultado quando:

- proporções mudarem entre direções;
- acessórios desaparecerem ou trocarem de lado sem motivo;
- materiais variarem drasticamente entre frames;
- silhueta perder legibilidade;
- personagem for cortado pelo enquadramento;
- sombra ou iluminação mudarem de forma incoerente;
- referências culturais forem usadas sem contexto ou de forma estereotipada.

## 8. Adendo de 2026-11-06 — decisões D2 e D3

- Proporção canônica do personagem jogável: **3,5 cabeças** (`library/profiles/proportions/humanoid_35h_v1.json`).
- Identidade: **fantasia original**, sem representar diretamente nenhuma comunidade indígena específica. Elementos culturais reais não são combinados sem pesquisa e revisão.
- Forma é avaliada em argila antes de qualquer textura.

## 9. Adendo de 2026-11-07: Procedural Art Direction System

- **Perfil principal:** `pindorama_friendly_smooth_v1`. Ilustração digital suave, formas arredondadas e volumes orgânicos, contorno artístico controlado (espessura variável, cor da peça escurecida), sombras suaves, highlights direcionados, texturas discretas, paleta harmônica e isometria consistente. **Não é pixel art.**
- **Perfil opcional:** `pindorama_pixel_art_detailed_v1`. Fica disponível, mas não é a direção principal (conflito C1 na matriz).
- **Histórico:** `pindorama_stylized_v1` (toon com casca 3D, reprovado no G9) e `pindorama_chibi_v1` (protótipo do Aprendiz).
- **Parâmetros centralizados:** iluminação, sombras, papéis de material (tons, matiz, brilho, padrão), contorno, resolução e escala. Todo gerador consome o perfil e não define paleta ou luz próprias.
- **Referências de avaliação, nunca incorporadas aos assets:**
  - Mago e Coquinho (identidade);
  - Duende (nível de detalhe em roupa, cabelo, acessórios e materiais);
  - Saci (expressividade e personalidade).
  As três estão em `Pindorama/[Old] Pindorama Game/design/`.
- **Proporção:** o chibi (~2,3 cabeças) segue o alvo atual. D2 (3,5 cabeças) aguarda revogação formal.
