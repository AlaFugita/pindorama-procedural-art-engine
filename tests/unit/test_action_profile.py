"""Perfil de animação com ações: regras que o controlador do Godot assume."""

import json
from pathlib import Path

import pytest

from app.schemas.contracts import AnimationClip, AnimationProfile

PROFILE = Path(__file__).resolve().parents[2] / "library/animations/humanoid_chibi_basic_v1.json"


@pytest.fixture(scope="module")
def clips():
    data = AnimationProfile.model_validate(json.loads(PROFILE.read_text(encoding="utf-8")))
    return {c.animation_id: c for c in data.clips}


def test_locomotion_loops_and_actions_do_not(clips):
    for name in ("idle", "walk", "run"):
        assert clips[name].loop and clips[name].priority == 0 and not clips[name].keys
    for name in ("attack_melee", "cast", "interact", "hurt", "death"):
        assert not clips[name].loop and clips[name].keys and clips[name].priority > 0


def test_action_rules_are_consistent(clips):
    for clip in clips.values():
        if clip.loop:
            continue
        assert clip.interruptible_after < clip.frame_count or clip.return_to is None
        assert clip.return_to is None or clip.return_to in clips
        assert all(0 <= f < clip.frame_count for f in clip.held_frames)
        for phase in clip.phases:
            assert 0 <= phase.start_frame <= phase.end_frame < clip.frame_count
    assert clips["death"].return_to is None and clips["death"].priority > clips["hurt"].priority > clips["attack_melee"].priority


def test_gameplay_events_mark_the_moment_of_effect(clips):
    expected = {"attack_melee": "HIT", "cast": "CAST_RELEASE", "interact": "INTERACT", "hurt": "IMPACT", "death": "DEATH_REST"}
    for name, event in expected.items():
        assert any(e.event == event for e in clips[name].events), name


def test_action_id_pattern_rejects_garbage():
    base = json.loads(PROFILE.read_text(encoding="utf-8"))["clips"][0]
    with pytest.raises(ValueError):
        AnimationClip.model_validate({**base, "animation_id": "Attack Melee!"})
