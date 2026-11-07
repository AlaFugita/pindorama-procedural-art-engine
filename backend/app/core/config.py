"""Descoberta de ferramentas e caminhos. Nunca presume caminho fixo da máquina.

Ordem: variável de ambiente (ICS_BLENDER/ICS_GODOT) → pasta local ``tools/`` → PATH.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(os.environ.get("ICS_ROOT", Path(__file__).resolve().parents[3]))
TOOLS_DIR = REPO_ROOT / "tools"
LIBRARY_DIR = REPO_ROOT / "library"
BLENDER_SCRIPTS = REPO_ROOT / "blender" / "scripts"
GODOT_TEMPLATE = REPO_ROOT / "integrations" / "godot" / "demo_project"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
PROJECTS_DIR = Path(os.environ.get("ICS_PROJECTS", REPO_ROOT / "projects"))


class ToolNotFound(RuntimeError):
    pass


def _find(env_var: str, globs: list[str], path_names: list[str]) -> Path:
    if value := os.environ.get(env_var):
        path = Path(value)
        if path.is_file():
            return path
        raise ToolNotFound(f"{env_var} aponta para arquivo inexistente: {value}")
    for pattern in globs:
        matches = sorted(TOOLS_DIR.glob(pattern))
        if matches:
            return matches[-1]
    for name in path_names:
        if found := shutil.which(name):
            return Path(found)
    raise ToolNotFound(f"ferramenta não encontrada; defina {env_var} (ver docs/SETUP_WINDOWS.md)")


def find_blender() -> Path:
    return _find("ICS_BLENDER", ["blender-*/blender.exe", "blender-*/blender"], ["blender"])


def find_godot() -> Path:
    return _find(
        "ICS_GODOT",
        ["godot/Godot_*_console.exe", "godot/Godot_*"],
        ["godot", "godot4"],
    )


def tool_version(executable: Path, *args: str) -> str:
    done = subprocess.run(
        [str(executable), *args], capture_output=True, text=True, timeout=120, check=True,
        encoding="utf-8", errors="replace",
    )
    lines = [line.strip() for line in done.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"sem saída de versão: {executable.name}")
    return lines[0] if "blender" in executable.name.lower() else lines[-1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(data: Any) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
