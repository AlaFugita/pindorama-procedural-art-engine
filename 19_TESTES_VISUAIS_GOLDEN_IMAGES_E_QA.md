# 19 — Testes visuais, golden images e QA

## 1. Objetivo

Definir como testar as imagens exportadas e como detectar regressões de render sem fingir que uma comparação de pixels compreende a intenção artística.

## 2. Golden assets

Manter uma pequena biblioteca de referência aprovada:

- um personagem humanoide base;
- uma pose neutra;
- poses sentinela de cada membro;
- uma ação idle;
- uma ação walk;
- uma ação run;
- renders das oito direções;
- imagem com marcadores e eixos para QA.

Cada golden asset registra Blender/version, rig version, render profile, resolução, frame, direção, materiais e seed quando houver IA. Mudança intencional de aparência exige aprovação humana e atualização explícita do baseline; não atualizar golden images automaticamente após falha.

## 3. Verificações automatizáveis de imagem

### 3.1 Arquivo

- PNG decodifica;
- canal RGBA presente quando esperado;
- dimensão corresponde ao perfil;
- tamanho de arquivo não é zero;
- ausência de corrupção;
- perfil de cor declarado/consistente.

### 3.2 Transparência

- fundo esperado é transparente;
- alpha não está totalmente zerado;
- máscara de personagem existe;
- não existe fundo opaco não intencional;
- bordas sem halos indesejados, conforme teste visual e perfil de composição.

### 3.3 Enquadramento

- silhueta não toca margem de segurança;
- nenhum componente foi cortado;
- bounding box dentro da área permitida;
- pivot de chão é consistente;
- padding segue configuração;
- quadro não contém pixels fora da região esperada.

O pivot deve vir da origem/ground marker 3D projetada, não de escolher automaticamente o pixel inferior da silhueta. Armas, cabelos, asas ou efeitos podem se estender mais que os pés.

### 3.4 Atlas e frames

- número de frames corresponde ao manifesto;
- retângulos não se sobrepõem indevidamente;
- UV/retângulos não ultrapassam atlas;
- padding/gutter obedece ao preset;
- ordem de frames explícita;
- nenhum frame duplicado por erro de pipeline, salvo repetição intencional documentada.

## 4. Comparação visual

Usar comparações em níveis:

1. igualdade exata de parâmetros da cena;
2. diferença absoluta de pixels para alterações determinísticas;
3. SSIM/perceptual metrics ou comparação de silhueta para tolerar variação de render quando justificável;
4. landmarks semânticos projetados;
5. revisão humana.

As métricas são indicadores e não veredictos artísticos. Iluminação, ruído, antialiasing e mudanças de versão podem causar diferenças legítimas. As tolerâncias precisam ser calibradas e registradas.

## 5. Oito direções: validação específica

Para cada direção:

- renderizar o marcador `FRONT` e os marcadores `CHAR_LEFT`/`CHAR_RIGHT` em modo debug;
- confirmar que o heading e o nome do arquivo correspondem ao mapeamento;
- confirmar projeção da origem e dos landmarks;
- confirmar dimensões e pivot;
- gerar uma folha 3×3 com o centro reservado para a legenda ou referência neutra;
- comparar a folha com o baseline aprovado.

Não comparar as oito imagens exigindo simetria. A roupa e acessórios podem ser assimétricos. O objetivo é confirmar identidade de direção, consistência de modelo e integridade de projeção.

## 6. Limites de IA de visão

Um modelo multimodal pode responder perguntas como “há provável corte?”, “a arma parece ter desaparecido?” ou “a roupa parece divergir do concept?”. Esses resultados devem ser `AI_REVIEW_HINT`, nunca `PASS` definitivo.

Não usar um modelo de visão como único validador de:

- membro anatômico esquerdo/direito;
- hierarquia do rig;
- foot sliding;
- limite de rotação;
- compatibilidade do atlas;
- integridade do PNG;
- importação real no Godot.

Esses itens têm verificações determinísticas próprias.

## 7. Teste de regressão

Toda mudança em Blender scripts, render profile, câmera, materiais base, rig ou exporter deve rodar o conjunto de golden tests afetado. Guardar outputs de referência, diffs e logs em artefatos de teste.

## 8. Relatório visual

Criar um HTML ou Markdown com:

- miniaturas das imagens;
- baseline ao lado do resultado;
- overlay/diff;
- métricas;
- estado PASS/WARN/FAIL/REVIEW;
- versão do pipeline;
- link/caminho dos arquivos originais.

## 9. Critério de aceite

Não basta gerar PNG. É preciso executar QA de arquivo, alpha, recorte, pivot, ordem de frames e direção. A parte artística continua sujeita à revisão humana.
