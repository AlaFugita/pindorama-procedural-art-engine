"""BL-001, BL-002, RND-001, RND-002, IMG-001 + falhas do worker."""

import time
from pathlib import Path

import pytest
from app.core.config import LIBRARY_DIR, read_json
from app.domain.directions import camera_basis
from app.schemas.contracts import RenderProfile
from app.workers import blender_worker
from app.workers.blender_worker import BlenderStageError, run_stage

from engines.postprocess_engine.images import alpha_bbox, check_png, load_rgba

pytestmark = pytest.mark.blender

RENDER_DATA = read_json(LIBRARY_DIR / "profiles" / "render" / "isometric_8dir_v1.json")
ART = read_json(LIBRARY_DIR / "profiles" / "art" / "pindorama_stylized_v1.json")


def smoke_payload(png: Path) -> dict:
    profile = RenderProfile.model_validate(RENDER_DATA)
    basis = camera_basis(profile)
    render = {
        **RENDER_DATA,
        "camera": {"matrix_world": basis.matrix_world(), "ortho_scale": basis.ortho_scale},
    }
    return {"render": render, "art": ART, "output_png": str(png)}


def assert_smoke(tmp: Path) -> None:
    png = tmp / "smoke.png"
    run = run_stage("smoke", smoke_payload(png), tmp / "work", timeout_s=180)
    assert run.exit_code == 0
    assert run.output["camera_type"] == "ORTHO"
    assert run.output["engine"] == "BLENDER_EEVEE"
    assert check_png(png, 256, 320, margin=2) == []
    rgba = load_rgba(png)
    x0, y0, x1, y1 = alpha_bbox(rgba)
    # Cubo de 0.6 m centrado no pivot horizontal: bbox simétrica em torno de x = 128.
    assert (x0 + x1) / 2 == pytest.approx(128, abs=1.5)
    # Largura exata: 0.6 m × 160 px/m.
    assert x1 - x0 == pytest.approx(96, abs=2)


def test_smoke_render(tmp_path):
    assert_smoke(tmp_path)


def test_path_with_spaces_and_non_ascii(tmp_path):
    assert_smoke(tmp_path / "pasta com espaço" / "guardião ção")


def test_worker_reports_python_failure(tmp_path):
    with pytest.raises(BlenderStageError, match="exit code") as info:
        run_stage("does_not_exist", {}, tmp_path, timeout_s=60)
    assert info.value.log_path.read_text(encoding="utf-8").strip()
    assert "ModuleNotFoundError" in info.value.log_path.read_text(encoding="utf-8")


def test_worker_timeout_kills_process(tmp_path):
    started = time.monotonic()
    with pytest.raises(BlenderStageError, match="timeout"):
        run_stage("smoke", smoke_payload(tmp_path / "x.png"), tmp_path, timeout_s=0.2)
    assert time.monotonic() - started < 15


def test_missing_tool_is_explicit(monkeypatch):
    from app.core import config

    monkeypatch.setenv("ICS_BLENDER", "C:/inexistente/blender.exe")
    with pytest.raises(config.ToolNotFound):
        blender_worker.find_blender()
