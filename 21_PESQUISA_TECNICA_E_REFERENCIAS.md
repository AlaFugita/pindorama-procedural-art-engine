# 21 — Pesquisa técnica e referências oficiais

## 1. Instrução ao agente

As fontes abaixo são referências iniciais consultadas na preparação desta documentação. O agente de implementação deve abri-las novamente, verificar a versão atual e procurar documentação adicional quando necessário. URLs podem mudar; se um link falhar, localize a página equivalente no domínio oficial e registre a substituição.

Não usar somente snippets de buscadores. Abrir a página primária, verificar versão e contexto. Registrar a data da consulta e a versão efetiva instalada.

## 2. Blender — API, rigging e execução automatizada

### Python API: Armatures e bones

https://docs.blender.org/api/main/info_gotchas_armatures_and_bones.html

Relevância:
- diferencia `Edit Bones`, `Bone` e `Pose Bones`;
- esclarece que transformações, constraints e IK da pose ficam nos pose bones;
- importante para scripts que criam/validam rigs.

### Manual de posing e IK

https://docs.blender.org/manual/en/latest/animation/armatures/posing/index.html

https://docs.blender.org/manual/en/latest/animation/armatures/posing/bone_constraints/inverse_kinematics/introduction.html

Relevância:
- constraints, limits e IK;
- compreender as capacidades e as limitações antes de criar rigs por script.

### Câmeras e projeção ortográfica

https://docs.blender.org/manual/en/latest/render/cameras.html

Relevância:
- câmera ortográfica;
- escala e enquadramento;
- diferença entre projeção ortográfica e perspectiva.

### Linha de comando/background

https://docs.blender.org/manual/pt/latest/advanced/command_line/arguments.html

https://docs.blender.org/manual/en/latest/advanced/command_line/

Relevância:
- executar Blender em background;
- renderizar frames/animações;
- automatizar sem depender de cliques na interface.

### Developer documentation — armatures

https://developer.blender.org/docs/features/animation/armatures/

Relevância:
- hierarquia, rest pose, pose space e transform spaces.

## 3. Godot — sprites e animação 2D

### AnimatedSprite2D

https://docs.godotengine.org/en/stable/classes/class_animatedsprite2d.html

### SpriteFrames

https://docs.godotengine.org/en/stable/classes/class_spriteframes.html

### Tutorial de animação 2D

https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html

### Image

https://docs.godotengine.org/en/stable/classes/class_image.html

Relevância:
- importar frames individuais ou sheets;
- construir recursos SpriteFrames;
- configurar e reproduzir animações;
- validar imagens e formatos.

O agente deve conferir a versão do Godot realmente escolhida pelo projeto. Não presumir que a documentação `stable` corresponde a qualquer instalação antiga.

## 4. glTF — formato de intercâmbio 3D

### Registry oficial

https://registry.khronos.org/glTF/

### Especificação glTF 2.0

https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

### Repositório e ferramentas Khronos

https://github.com/KhronosGroup/glTF

Relevância:
- eixos e unidades;
- nodes, scenes, meshes, materials;
- skins, joints, weights e animações;
- objetivos de formato de entrega runtime;
- ferramentas de validação e modelos de referência.

A convenção de eixos deve ser respeitada e convertida em um único adaptador. `.blend` permanece o arquivo-fonte de autoria; GLB é formato de intercâmbio/entrega, não substituto de todos os dados de autoria.

## 5. ComfyUI — workflows e integração opcional

### Exemplo oficial de WebSocket API

https://github.com/Comfy-Org/ComfyUI/blob/master/script_examples/websockets_api_example.py

### API/OpenAPI do repositório oficial

https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml

Relevância:
- submeter workflow;
- acompanhar execução;
- obter outputs;
- evitar acoplamento à interface web.

Antes de integrar, verificar o contrato atual no repositório oficial. Endpoints podem mudar e alguns podem estar depreciados. A integração ComfyUI é opcional e não pode ser necessária para o pipeline de render 3D funcionar.

## 6. Política de versões

Na primeira execução do projeto, registrar:

- sistema operacional e arquitetura;
- Python e ambiente virtual;
- Blender versão e build;
- Godot versão e build;
- Node e package manager;
- Tauri versão;
- dependências Python/JS;
- drivers/GPU relevantes quando usados.

Fixar versões compatíveis em arquivos de dependência/lock. Atualizações devem ser deliberadas e cobertas por testes.

## 7. Como pesquisar uma dúvida técnica

1. formular a pergunta técnica concreta;
2. identificar o componente responsável;
3. buscar documentação oficial/API/specification;
4. abrir e confirmar que o recurso existe na versão-alvo;
5. criar um pequeno protótipo se comportamento for ambíguo;
6. registrar conclusão e URL;
7. adicionar teste de regressão para comportamento crítico.

## 8. Log mínimo de pesquisa

Criar `docs/research/RESEARCH_LOG.md` com campos:

| Data | Pergunta | Fonte oficial | Versão verificada | Conclusão | Decisão/código afetado |
|---|---|---|---|---|---|

Não escrever “pesquisado na internet” sem registrar o que foi consultado.
