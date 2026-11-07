# Relatório de ambiente

Levantado em 2026-11-06. Reproduza com `uv run ics doctor`.

| Item | Valor |
|---|---|
| Sistema | Windows 11 Pro 10.0.26200, x64 |
| CPU | AMD Ryzen 7 5700X |
| RAM | 32 GB |
| GPU | NVIDIA GeForce RTX 5060, 8 GB, driver 610.88 |
| Python | 3.13 em `.venv`, fixado por `.python-version` e `uv.lock` |
| Node | 24.22 |
| Blender | 5.2.3 LTS portátil em `tools/` (build e13b728c6880) |
| Godot | 4.7.2 stable em `tools/godot` |
| Rust / Tauri | Não instalados (fase congelada) |

**Blender:** `blender-5.2.3-windows-x64.zip`, 405.839.452 bytes, de download.blender.org, SHA-256 `723f08a4401502561eb763cdeacf8745b31e5f3f154d287d3830d97cf75dc2fb` conferido com o arquivo oficial.

**Repositório:** não era Git; só havia a documentação, preservada intacta. `git init` executado, sem commits.

**Limite relevante:** 8 GB de VRAM impede modelos image-to-3D completos localmente; ver a auditoria.

## Executar no Windows

```bash
uv sync --extra dev
```

```bash
uv run ics doctor
```

```bash
uv run ics run tests/fixtures/specs/guardiao_da_floresta.json
```

```bash
uv run pytest -q
```

Para usar outra instalação, defina `ICS_BLENDER` e `ICS_GODOT`. A pasta `tools/` não é versionada: em outra máquina, instale as ferramentas e aponte essas variáveis.
