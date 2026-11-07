"""D2 (proporção versionada), regra 6 (histórico de reprovação) e worker com caminho relativo."""

import importlib.util
import json
import sys

import pytest
from app.core.config import BLENDER_SCRIPTS, LIBRARY_DIR, read_json
from app.schemas.contracts import ProportionProfile
from app.services.approvals import record
from pydantic import ValidationError

PROFILE_PATH = LIBRARY_DIR / "profiles" / "proportions" / "humanoid_35h_v1.json"


def load_segments():
    spec = importlib.util.spec_from_file_location(
        "master_body", BLENDER_SCRIPTS / "ics_blender" / "master_body.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["master_body"] = module
    spec.loader.exec_module(module)
    return {segment["name"]: segment for segment in module.SEGMENTS}


def test_profile_is_35_heads():
    profile = ProportionProfile.model_validate(read_json(PROFILE_PATH))
    assert profile.height_m / profile.head_height_m == pytest.approx(3.5, abs=0.05)


def test_profile_rejects_incoherent_head():
    data = read_json(PROFILE_PATH)
    data["head_height_m"] = 0.30
    with pytest.raises(ValidationError):
        ProportionProfile.model_validate(data)


def test_route_a_targets_match_profile():
    profile = ProportionProfile.model_validate(read_json(PROFILE_PATH))
    segments = load_segments()
    assert segments["head"]["dst"][0][2] == pytest.approx(profile.chin_z_m)
    assert segments["head"]["dst"][1][2] == pytest.approx(profile.height_m)
    assert segments["thigh"]["dst"][0][2] == pytest.approx(profile.hip_z_m)
    assert segments["thigh"]["dst"][1][2] == pytest.approx(profile.knee_z_m)
    assert segments["upper_arm"]["dst"][0][0] == pytest.approx(profile.shoulder_half_width_m)


def test_rejection_survives_later_approval(tmp_path):
    (tmp_path / "character_spec.json").write_text(json.dumps({"id": "x"}), encoding="utf-8")
    record(tmp_path, "G9", "REJECTED", "usuario", "reprovado")
    record(tmp_path, "G9", "APPROVED", "usuario", "novo mestre")
    data = read_json(tmp_path / "approvals.json")
    assert data["G9"]["status"] == "APPROVED"
    assert [h["status"] for h in data["history"]] == ["REJECTED"]
    assert data["history"][0]["gate"] == "G9"


@pytest.mark.blender
def test_worker_accepts_relative_work_dir(tmp_path, monkeypatch):
    from app.workers.blender_worker import BlenderStageError, run_stage

    monkeypatch.chdir(tmp_path)
    with pytest.raises(BlenderStageError, match="exit code") as info:
        run_stage("does_not_exist", {}, __import__("pathlib").Path("rel"), timeout_s=60)
    assert "ModuleNotFoundError" in info.value.log_path.read_text(encoding="utf-8")
