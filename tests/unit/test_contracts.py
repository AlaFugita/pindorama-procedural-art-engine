"""SPEC-001, SPEC-002, DIR-001 e invariantes de status."""

import copy

import pytest
from app.core.config import LIBRARY_DIR, read_json
from app.schemas.contracts import (
    DIRECTION_ORDER,
    CharacterSpec,
    CheckResult,
    ExportManifest,
    GateStatus,
    RenderProfile,
    aggregate,
    utcnow,
)
from pydantic import ValidationError

GUARDIAN = {
    "schema_version": "1.0.0",
    "id": "character_001",
    "name": "Guardião da Floresta",
    "slug": "guardiao_da_floresta",
    "family": "humanoid",
    "art_profile": "pindorama_stylized_v1",
    "body_profile": {"asset_id": "humanoid_compact_v1", "scale": 1.0, "proportions": "chibi_moderate"},
    "appearance": {
        "head_asset": "head_round_v1",
        "hair_asset": "hair_long_tied_v1",
        "skin_material": "skin_warm_01",
        "face_preset": "face_guardian_01",
    },
    "outfit": {
        "body_asset": "outfit_natural_fabric_01",
        "accessories": ["feather_ornament_01", "necklace_01"],
        "weapon_asset": "spear_wood_01",
    },
    "palette": {"primary": "#A94D2D", "secondary": "#4D3025", "accent": "#E5B36C"},
    "rig_profile": "humanoid_standard_v1",
    "animation_profile": "humanoid_basic_v1",
    "render_profile": "isometric_8dir_v1",
}


def test_spec_valid():
    spec = CharacterSpec.model_validate(GUARDIAN)
    assert spec.slug == "guardiao_da_floresta"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(unknown_field=1),
        lambda d: d["body_profile"].update(extra=True),
        lambda d: d.pop("rig_profile"),
        lambda d: d.update(slug="Com Espaço"),
        lambda d: d["palette"].update(primary="red"),
        lambda d: d.update(family="dragon"),
        lambda d: d.update(schema_version="2.0.0"),
        lambda d: d["outfit"].update(accessories=["a", "a"]),
    ],
)
def test_spec_rejects(mutate):
    data = copy.deepcopy(GUARDIAN)
    mutate(data)
    with pytest.raises(ValidationError):
        CharacterSpec.model_validate(data)


def render_data():
    return read_json(LIBRARY_DIR / "profiles" / "render" / "isometric_8dir_v1.json")


def test_render_profile_loads_with_eight_directions():
    profile = RenderProfile.model_validate(render_data())
    assert tuple(profile.direction_order) == DIRECTION_ORDER
    assert len(set(profile.headings_deg.values())) == 8


def test_render_profile_rejects_swapped_headings():
    data = render_data()
    data["headings_deg"]["E"], data["headings_deg"]["W"] = 270, 90
    with pytest.raises(ValidationError, match="heading"):
        RenderProfile.model_validate(data)


def test_render_profile_rejects_wrong_order():
    data = render_data()
    data["direction_order"][0], data["direction_order"][1] = "NE", "N"
    with pytest.raises(ValidationError, match="ordem"):
        RenderProfile.model_validate(data)


def check(status):
    return CheckResult(id="X", status=status)


def test_not_tested_never_becomes_pass():
    assert aggregate([check(GateStatus.PASS), check(GateStatus.NOT_TESTED)]) is GateStatus.NOT_TESTED
    assert aggregate([]) is GateStatus.NOT_TESTED
    assert aggregate([check(GateStatus.PASS), check(GateStatus.FAIL)]) is GateStatus.FAIL
    assert aggregate([check(GateStatus.PASS), check(GateStatus.REVIEW)]) is GateStatus.REVIEW


def test_production_requires_approval():
    with pytest.raises(ValidationError, match="production"):
        ExportManifest(
            character_id="c", character_name="c", character_revision=1, art_profile="a",
            render_profile="r", rig_profile="g", animation_profile="n", release="production",
            approval="UNAPPROVED", exporter_version="0", blender_version="0", target="godot",
            tested_compatibility=None, created_at=utcnow(),
            direction_order=list(DIRECTION_ORDER), animations=[], files=[],
        )
