"""Inventário do ambiente e gate G0 (ENV-001). Não expõe caminhos pessoais."""

from __future__ import annotations

import platform
import shutil
from pathlib import Path
from typing import Any

from app.core.config import REPO_ROOT, ToolNotFound, find_blender, find_godot, tool_version
from app.workers.blender_worker import run_stage

SUPPORTED = {"blender": "5.2", "godot": "4.7"}


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def collect() -> dict[str, Any]:
    report: dict[str, Any] = {
        "os": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "node": shutil.which("node") is not None,
        "tools": {},
        "ok": True,
    }
    for name, finder, args in (
        ("blender", find_blender, ("--version",)),
        ("godot", find_godot, ("--version", "--headless")),
    ):
        try:
            executable = finder()
            version = tool_version(executable, *args)
        except (ToolNotFound, OSError) as error:
            report["tools"][name] = {"found": False, "error": str(error)}
            report["ok"] = False
            continue
        supported = SUPPORTED[name] in version
        report["tools"][name] = {
            "found": True, "path": _display(executable), "version": version, "supported": supported,
        }
        report["ok"] = report["ok"] and supported
    return report


__all__ = ["collect", "run_stage"]
