# 06 — Contratos de dados

## 1. Princípios

- Todo contrato deve ter `schema_version`.
- IDs devem ser estáveis e não depender do nome visível.
- Caminhos armazenados no banco devem ser relativos ao projeto sempre que possível.
- A origem e versão de cada asset devem ser rastreáveis.
- Alterações incompatíveis exigem nova versão de schema e migração.
- Exemplos deste documento são rascunhos e precisam ser convertidos em modelos Pydantic e JSON Schema testados.

## 2. CharacterSpec

Define a identidade e a configuração desejada do personagem.

```json
{
  "schema_version": "1.0.0",
  "id": "character_001",
  "name": "Guardiao da Floresta",
  "slug": "guardiao_da_floresta",
  "family": "humanoid",
  "art_profile": "pindorama_stylized_v1",
  "body_profile": {
    "asset_id": "humanoid_compact_v1",
    "scale": 1.0,
    "proportions": "chibi_moderate"
  },
  "appearance": {
    "head_asset": "head_round_v1",
    "hair_asset": "hair_long_tied_v1",
    "skin_material": "skin_warm_01",
    "face_preset": "face_guardian_01"
  },
  "outfit": {
    "body_asset": "outfit_natural_fabric_01",
    "accessories": ["feather_ornament_01", "necklace_01"],
    "weapon_asset": "spear_wood_01"
  },
  "palette": {
    "primary": "#A94D2D",
    "secondary": "#4D3025",
    "accent": "#E5B36C"
  },
  "rig_profile": "humanoid_standard_v1",
  "animation_profile": "humanoid_basic_v1",
  "render_profile": "isometric_8dir_v1"
}
```

### Campos essenciais

| Campo | Tipo | Regra |
|---|---|---|
| `schema_version` | string | versão do contrato |
| `id` | string | ID único e estável |
| `name` | string | nome de exibição |
| `slug` | string | identificador seguro para diretórios |
| `family` | enum/string | família corporal |
| `art_profile` | string | perfil visual versionado |
| `body_profile` | object | corpo e escala |
| `appearance` | object | cabeça, cabelo, pele e rosto |
| `outfit` | object | roupas, acessórios e armas |
| `rig_profile` | string | rig compatível |
| `animation_profile` | string | conjunto de animações |
| `render_profile` | string | câmera e renderização |

## 3. BuildManifest

Registra como a cena 3D foi montada.

Campos recomendados:
- `schema_version`;
- `character_id`;
- `builder_version`;
- `blender_version`;
- `source_scene`;
- lista de assets e respectivas versões;
- materiais aplicados;
- transformações e pontos de ancoragem;
- avisos de compatibilidade;
- hash dos arquivos relevantes.

## 4. RigProfile

Registra a família de esqueleto.

Campos recomendados:
- `id` e `version`;
- `family`;
- `skeleton_asset`;
- hierarquia esperada;
- nomes de ossos obrigatórios;
- convenções de orientação;
- escala de referência;
- animações compatíveis;
- validações específicas.

## 5. AnimationProfile

Campos recomendados:
- `id` e `version`;
- `rig_profile` compatível;
- lista de clips;
- FPS padrão;
- loop padrão;
- frame inicial/final;
- política de root motion;
- notas de sincronização e eventos.

## 6. RenderProfile

Campos recomendados:
- `id` e `version`;
- tipo de projeção;
- elevação e azimute de referência;
- resolução de frame;
- resolução de saída;
- margem de segurança;
- fundo transparente;
- perfil de iluminação;
- ponto de apoio;
- ordem das oito direções;
- convenção de orientação.

## 7. GenerationJob

Exemplo simplificado:

```json
{
  "id": "job_000123",
  "project_id": "project_001",
  "character_id": "character_001",
  "type": "render_character",
  "status": "RUNNING",
  "current_stage": "RENDERING",
  "progress": 0.45,
  "created_at": "2026-11-06T12:00:00Z",
  "updated_at": "2026-11-06T12:02:00Z",
  "input_manifest": "jobs/job_000123/input.json",
  "output_dir": "jobs/job_000123/output",
  "error": null
}
```

O campo `progress` é opcional e estimado. Não deve ser apresentado como precisão absoluta quando as etapas têm custos diferentes.

## 8. ExportManifest

Deve conter:
- versão do schema;
- personagem e versão;
- perfil artístico;
- perfil de renderização;
- animações exportadas;
- ordem de direções;
- FPS e loop por animação;
- arquivos gerados e hashes;
- dimensões de frame e atlas;
- pivôs;
- versão do Exporter;
- destino e compatibilidade testada.

## 9. Versionamento

Usar versionamento semântico para schemas e componentes quando apropriado:

- mudança compatível: incremento de versão menor;
- correção sem quebra de contrato: patch;
- mudança incompatível: versão maior e migração.

A convenção final deve ser validada quando os schemas Pydantic forem criados.
