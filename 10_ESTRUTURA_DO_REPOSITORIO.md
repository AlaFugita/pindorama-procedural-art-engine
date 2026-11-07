# 10 — Estrutura do repositório

## 1. Proposta de monorepositório

```text
isometric-character-studio/
├── apps/
│   └── desktop/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── features/
│       │   └── services/
│       ├── src-tauri/
│       └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── jobs/
│   │   └── workers/
│   ├── migrations/
│   └── pyproject.toml
├── engines/
│   ├── character_engine/
│   ├── ai_engine/
│   ├── model_engine/
│   ├── rig_engine/
│   ├── animation_engine/
│   ├── render_engine/
│   ├── postprocess_engine/
│   └── export_engine/
├── blender/
│   ├── scripts/
│   ├── templates/
│   ├── startup/
│   └── tests/
├── library/
│   ├── assets/
│   ├── components/
│   ├── materials/
│   ├── rigs/
│   ├── animations/
│   └── profiles/
├── integrations/
│   ├── godot/
│   └── ai_providers/
├── projects/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── blender/
│   ├── render_regression/
│   └── fixtures/
├── docs/
├── scripts/
├── .gitignore
├── README.md
└── pyproject.toml
```

## 2. Responsabilidades dos diretórios

| Diretório | Responsabilidade |
|---|---|
| `apps/desktop` | Interface desktop e shell Tauri |
| `backend` | API local, domínio, persistência e jobs |
| `engines` | Serviços de domínio especializados |
| `blender` | Scripts e templates executados pelo Blender |
| `library` | Conteúdo 3D versionado e metadados |
| `integrations` | Adaptadores para Godot e providers de IA |
| `projects` | Projetos de usuário; normalmente fora do controle de versão |
| `tests` | Testes automatizados e fixtures |
| `docs` | Documentação do produto e engenharia |
| `scripts` | Automação de desenvolvimento e empacotamento |

## 3. Regras de organização

- Evitar dependência circular entre engines.
- Contratos compartilhados devem ficar em um local explícito e versionado.
- O código de interface não deve importar módulos Blender.
- Scripts Blender devem aceitar argumentos de entrada e produzir manifesto de saída.
- Conteúdo da biblioteca deve ter `asset.json` ou metadados equivalentes.
- Projetos do usuário e arquivos gerados não devem ser commitados por padrão.
- Test fixtures pequenas devem ser commitadas para garantir testes reproduzíveis.

## 4. Convenção de nomes

- Python: `snake_case`;
- TypeScript/React: `camelCase` para funções e `PascalCase` para componentes;
- contratos JSON: `snake_case`;
- IDs: estáveis, não derivados exclusivamente de nomes editáveis;
- arquivos de direção: sufixos padronizados `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`.

## 5. Separação entre código e conteúdo

A biblioteca 3D é conteúdo do produto. Seu versionamento deve considerar tamanho dos arquivos e licenças. Avaliar Git LFS ou armazenamento de artefatos quando os arquivos crescerem. Não armazenar modelos pesados em commits comuns sem estratégia definida.
