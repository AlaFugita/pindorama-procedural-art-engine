from __future__ import annotations

import pytest
from app.core.config import ToolNotFound, find_blender, find_godot


def _has(finder) -> bool:
    try:
        finder()
    except ToolNotFound:
        return False
    return True


def pytest_collection_modifyitems(items):
    """Ferramenta ausente vira skip explícito (NOT_TESTED), nunca aprovação."""
    missing = {"blender": not _has(find_blender), "godot": not _has(find_godot)}
    for item in items:
        for marker, absent in missing.items():
            if absent and item.get_closest_marker(marker):
                item.add_marker(pytest.mark.skip(reason=f"{marker} indisponível"))
