# Mapa de oportunidades na arquitetura existente

Liga cada descoberta (F1–F11, em [technical-findings.md](technical-findings.md)) a um componente do PPAE que **já existe**. Nenhuma oportunidade exige módulo novo de fundação.

| Descoberta | Classificação | Componente afetado | O que falta | Dependências | Impacto | Integração proposta |
|---|---|---|---|---|---|---|
| F1 Seed + rascunho → final | **Parcial** | `CharacterSpec`, `pipeline._stage` | Campo `seed` na ficha; modo rascunho no build; detalhe pela resolução | Contrato | Baixo: novo campo opcional; o cache já inclui a ficha | `seed: int = 0` em `CharacterSpec`; `detail_by_canvas` no perfil |
| F2 Material como grafo de nós | **Oportunidade de melhoria** | `stage_pixel_passes._pattern`, papéis de material | Padrão contínuo combinável (ruído + costura + desgaste) | Nenhuma | Médio: muda o canal B do passe de luz | `pattern` passa a ser uma lista de camadas; mini NodeWrangler em `ics_blender/nodes.py` |
| F3 Grafo → shader do Godot | **Nova capacidade** | `export_engine/godot_bridge.py`, demo do Godot | Passe de máscara de material exportado + `.gdshader` de tingimento | Passe `id` (existe) | Médio: novo arquivo exportado por personagem | Exportar `*_mask.png` + `material_tint.gdshader` |
| F4 Curva com conicidade e ramificação | **Parcial** | `master_costume.strip`, `chibi_detail` | Curva com raio, torção e ramificação genérica | Nenhuma | Baixo | Função `branch_curve` em `geometry.py`, reutilizada no cabelo agora e na natureza depois |
| F5 Impostor por render offline | **Já implementada** (é o próprio PPAE) | Render + atlas | — | — | — | — |
| F6 SDF para formas | **Parcial** (voxel remesh) | `stage_build._make_mesh`, `chibi_detail` | Recorte 2D por SDF para barras e pontas | Nenhuma | Baixo | `sdf_outline` em `geometry.py` |
| F7 Luz única do perfil | **Já implementada** (personagens) | `ArtProfile.lights` | Garantia para os geradores futuros | Novos geradores | — | Regra no §3.2 do doc 03 (já escrita) |
| F8 Paleta em três níveis | **Já implementada** | `pixel.ramp` | — | — | — | — |
| F9 WFC e BSP | **Já planejada como visão** | Building e Environment (futuros) | Tudo | Fundação aprovada | Alto, futuro | Estudar posteriormente |
| F10 Asset = função; troca de pack | **Já implementada** | Ficha + gerador + `ArtProfile` | — | — | — | — |
| F11 Auditoria de catálogo | **Já planejada** (§13.4) | Futuro catálogo | Índice global de assets gerados | Catálogo | Baixo | `scripts/catalog.py` lendo `projects/*` e `exports/*` |
| Weber-Penn completo (midori) | **Já planejada como visão** | Nature Generator | Tudo | Fundação aprovada | — | Usar a CLI do midori como ferramenta externa (Apache-2.0) e renderizar o GLB no nosso pipeline |
| Material Maker como ferramenta | **Não aplicável agora** | — | — | — | — | Reavaliar se houver textura em imagem |
| texture-synthesis | **Não aplicável** | — | — | — | — | Arquivado; foge da geração por código |
