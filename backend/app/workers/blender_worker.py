"""Execução controlada do Blender em processo separado (doc 04 §4, doc 22 fase C).

Cada estágio recebe um JSON de entrada e deve gravar um JSON de saída. O sucesso só é
aceito com exit code 0 *e* ``status: ok`` no resultado: exit 0 sem manifesto é falha.
"""

from __future__ import annotations

import os
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import BLENDER_SCRIPTS, find_blender, read_json, write_json

ENTRYPOINT = BLENDER_SCRIPTS / "run_stage.py"
PY_FAILURE_EXIT = 17


class BlenderStageError(RuntimeError):
    def __init__(self, message: str, log_path: Path | None = None):
        super().__init__(message)
        self.log_path = log_path


@dataclass
class StageRun:
    stage: str
    exit_code: int
    seconds: float
    log_path: Path
    output: dict[str, Any]


def kill_tree(process: subprocess.Popen) -> None:
    """Encerra o processo e filhos; no Windows ``kill`` não alcança netos."""
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, check=False
        )
    else:
        process.kill()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def run_stage(
    stage: str,
    payload: dict[str, Any],
    work_dir: Path,
    *,
    blend_file: Path | None = None,
    timeout_s: float = 900.0,
    cancel: threading.Event | None = None,
    blender: Path | None = None,
) -> StageRun:
    work_dir = work_dir.resolve()  # o Blender roda com cwd=work_dir: caminho relativo quebraria
    work_dir.mkdir(parents=True, exist_ok=True)
    input_path = write_json(work_dir / f"{stage}.input.json", payload)
    output_path = work_dir / f"{stage}.output.json"
    log_path = work_dir / f"{stage}.log"
    output_path.unlink(missing_ok=True)

    command = [str(blender or find_blender()), "--background", "--factory-startup"]
    if blend_file is not None:
        command.append(str(blend_file))
    command += [
        "--python-exit-code", str(PY_FAILURE_EXIT),
        "--python", str(ENTRYPOINT),
        "--", "--stage", stage, "--input", str(input_path), "--output", str(output_path),
    ]

    started = time.monotonic()
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write("# " + " ".join(command) + "\n")
        log.flush()
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env,
            cwd=work_dir,
        )
        while process.poll() is None:
            if cancel is not None and cancel.is_set():
                kill_tree(process)
                raise BlenderStageError(f"{stage}: cancelado", log_path)
            if time.monotonic() - started > timeout_s:
                kill_tree(process)
                raise BlenderStageError(f"{stage}: timeout de {timeout_s:.0f}s", log_path)
            time.sleep(0.05)

    seconds = time.monotonic() - started
    if process.returncode != 0:
        raise BlenderStageError(f"{stage}: exit code {process.returncode}", log_path)
    if not output_path.is_file():
        raise BlenderStageError(f"{stage}: terminou sem manifesto de saída", log_path)
    output = read_json(output_path)
    if output.get("status") != "ok":
        raise BlenderStageError(f"{stage}: {output.get('error', 'status inválido')}", log_path)
    return StageRun(stage, process.returncode, seconds, log_path, output)
