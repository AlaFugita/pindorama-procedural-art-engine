"""Instala um pacote em uma cópia do projeto Godot e o exercita de verdade (GODOT-001/002).

O template versionado nunca é alterado: cada execução trabalha em cópia isolada.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from app.core.config import GODOT_TEMPLATE, find_godot, tool_version
from app.schemas.contracts import CheckResult, ExportManifest, GateStatus
from PIL import Image

CAPTURE_TOLERANCE = 3  # diferença máxima de canal por pixel entre captura e esperado
PLACE = (320, 400)
BACKGROUND = (59, 74, 66)


@dataclass
class GodotRun:
    version: str
    project: Path
    checks: list[CheckResult] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)


def _windowed(console_exe: Path) -> Path:
    """O *_console.exe mostra saída; para janela real usamos o mesmo binário de jogo."""
    return console_exe


def _run(command: list[str], log: Path, timeout: float) -> int:
    with log.open("a", encoding="utf-8", errors="replace") as stream:
        stream.write("# " + " ".join(command) + "\n")
        stream.flush()
        return subprocess.run(
            command, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout, check=False
        ).returncode


def prepare_project(package: Path, slug: str, work_dir: Path) -> Path:
    project = work_dir / "godot_project"
    if project.exists():
        shutil.rmtree(project)
    shutil.copytree(GODOT_TEMPLATE, project, ignore=shutil.ignore_patterns(".godot", "characters"))
    target = project / "characters" / slug
    target.mkdir(parents=True)
    shutil.copytree(package / "atlases", target / "atlases")
    shutil.copytree(package / "metadata", target / "metadata")
    shutil.copy2(package / "manifest.json", target / "manifest.json")
    shutil.copy2(package / "character.json", target / "character.json")
    return project


def compare_captures(package: Path, manifest: ExportManifest, capture_dir: Path, report: dict) -> list[str]:
    """Reconstrói o frame esperado a partir do atlas e compara com a tela capturada."""
    problems: list[str] = []
    animations = {a.animation: a for a in manifest.animations}
    for capture in report.get("captures", []):
        clip = capture["clip"]
        animation, direction = clip.rsplit("_", 1)
        atlas = animations[animation].directions[direction]
        rect = atlas.frames[capture["frame"]]
        with Image.open(package / "atlases" / atlas.file) as image:
            region = image.convert("RGBA").crop((rect.x, rect.y, rect.x + rect.w, rect.y + rect.h))
        source = Image.new("RGBA", (atlas.frame_width, atlas.frame_height), (0, 0, 0, 0))
        source.paste(region, (rect.ox, rect.oy))  # quadro cheio (atlas recortado ou não)
        shot_path = capture_dir / capture["file"]
        with Image.open(shot_path) as image:
            shot = np.asarray(image.convert("RGB"), dtype=int)
        left = round(PLACE[0] - atlas.pivot.x)
        top = round(PLACE[1] - atlas.pivot.y)
        expected = Image.new("RGBA", source.size, (*BACKGROUND, 255))
        expected.alpha_composite(source)
        expected_rgb = np.asarray(expected.convert("RGB"), dtype=int)
        h, w = expected_rgb.shape[:2]
        window = shot[top : top + h, left : left + w]
        if window.shape != expected_rgb.shape:
            problems.append(f"{capture['file']}: janela fora da tela")
            continue
        delta = np.abs(window - expected_rgb).max(axis=2)
        bad = int((delta > CAPTURE_TOLERANCE).sum())
        if bad > 0.002 * delta.size:
            problems.append(f"{capture['file']}: {bad} pixels divergem (máx {int(delta.max())})")
    return problems


def run_godot_checks(
    package: Path, manifest: ExportManifest, slug: str, work_dir: Path, *, windowed: bool = True
) -> GodotRun:
    godot = find_godot()
    version = tool_version(godot, "--version", "--headless")
    project = prepare_project(package, slug, work_dir)
    log = work_dir / "godot.log"
    log.unlink(missing_ok=True)
    run = GodotRun(version, project)
    resource = f"res://characters/{slug}"

    code = _run([str(godot), "--headless", "--path", str(project), "--import"], log, 300)
    result_path = work_dir / "godot_smoke.json"
    result_path.unlink(missing_ok=True)
    code_smoke = _run(
        [str(godot), "--headless", "--path", str(project), "--script", "res://smoke_test.gd",
         "--", "--package", resource, "--result", str(result_path)], log, 300,
    )
    if not result_path.is_file():
        run.checks.append(CheckResult(
            id="GODOT-001", status=GateStatus.FAIL,
            detail=f"sem relatório (import={code}, smoke={code_smoke})", evidence=[str(log)],
        ))
        return run
    smoke = json.loads(result_path.read_text(encoding="utf-8"))
    run.report["smoke"] = smoke
    failures = smoke["failures"]
    run.checks.append(CheckResult(
        id="GODOT-001",
        status=GateStatus.FAIL if failures or code_smoke else GateStatus.PASS,
        detail="; ".join(failures[:6]) or
        f"{smoke['godot']}: {smoke['clips']} clips, {smoke['frames']} frames, pixels idênticos",
        evidence=[str(result_path), str(log)],
    ))
    if not windowed:
        run.checks.append(CheckResult(id="GODOT-002", status=GateStatus.NOT_TESTED,
                                      detail="execução com janela não solicitada"))
        return run

    capture_dir = work_dir / "godot_capture"
    if capture_dir.exists():
        shutil.rmtree(capture_dir)
    capture_dir.mkdir()
    code_demo = _run(
        [str(godot), "--path", str(project), "--resolution", "640x480", "--",
         "--package", resource, "--capture", str(capture_dir)], log, 600,
    )
    report_path = capture_dir / "report.json"
    if not report_path.is_file():
        run.checks.append(CheckResult(id="GODOT-002", status=GateStatus.FAIL,
                                      detail=f"demo sem relatório (exit {code_demo})",
                                      evidence=[str(log)]))
        return run
    report = json.loads(report_path.read_text(encoding="utf-8"))
    run.report["runtime"] = {"captures": len(report["captures"]), "advanced": report["advanced"]}
    problems = list(report["failures"]) + compare_captures(package, manifest, capture_dir, report)
    expected = 2 * smoke["clips"]
    if len(report["captures"]) != expected:
        problems.append(f"{len(report['captures'])} capturas, esperadas {expected}")
    run.checks.append(CheckResult(
        id="GODOT-002",
        status=GateStatus.FAIL if problems else GateStatus.PASS,
        detail="; ".join(problems[:6]) or
        f"{len(report['captures'])} telas iguais ao frame esperado; {len(report['advanced'])} clips avançaram",
        tolerance=f"canal ≤ {CAPTURE_TOLERANCE}, até 0,2% dos pixels",
        evidence=[str(capture_dir)],
    ))
    return run


def record_video(project: Path, output: Path, seconds: int = 20) -> Path | None:
    godot = find_godot()
    fps = 30
    log = output.with_suffix(".log")
    code = _run(
        [str(godot), "--path", str(project), "--resolution", "640x480", "--write-movie", str(output),
         "--fixed-fps", str(fps), "--quit-after", str(seconds * fps)], log, 300,
    )
    return output if code == 0 and output.is_file() else None
