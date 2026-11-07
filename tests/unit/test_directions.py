"""DIR-001 e conversões de eixo: valores calculados à mão, independentes do código."""

import math

import pytest
from app.core.config import LIBRARY_DIR, read_json
from app.domain.directions import (
    camera_basis,
    canonical_to_gltf,
    heading_to_forward,
    project_canonical,
    project_world,
    rotate_to_heading,
    vector_to_direction,
)
from app.schemas.contracts import DIRECTION_ORDER, RenderProfile

PROFILE = RenderProfile.model_validate(
    read_json(LIBRARY_DIR / "profiles" / "render" / "isometric_8dir_v1.json")
)
LEFT_HAND = (-0.3, 0.0, 0.4)
RIGHT_HAND = (0.3, 0.0, 0.4)


def approx(a, b):
    assert a == pytest.approx(b, abs=1e-9)


@pytest.mark.parametrize(
    ("heading", "expected"),
    [(0, (0, 1, 0)), (90, (1, 0, 0)), (180, (0, -1, 0)), (270, (-1, 0, 0))],
)
def test_forward_compass(heading, expected):
    approx(heading_to_forward(heading), expected)
    approx(rotate_to_heading((0, 1, 0), heading), expected)


def test_origin_projects_to_pivot_in_all_headings():
    for name in DIRECTION_ORDER:
        x, y = project_canonical((0, 0, 0), PROFILE.headings_deg[name], PROFILE)
        approx((x, y), (PROFILE.pivot.x, PROFILE.pivot.y))


def test_south_view_left_hand_is_on_viewer_right():
    """Doc 17: em vista frontal a mão esquerda aparece à direita do observador."""
    left_x, _ = project_canonical(LEFT_HAND, 180, PROFILE)
    right_x, _ = project_canonical(RIGHT_HAND, 180, PROFILE)
    assert left_x > right_x


def test_north_view_left_hand_is_on_viewer_left():
    left_x, _ = project_canonical(LEFT_HAND, 0, PROFILE)
    right_x, _ = project_canonical(RIGHT_HAND, 0, PROFILE)
    assert left_x < right_x


def test_east_facing_character_left_hand_is_farther_up_screen():
    """Olhando para leste, a esquerda aponta para o norte: mais alto na tela."""
    _, left_y = project_canonical(LEFT_HAND, 90, PROFILE)
    _, right_y = project_canonical(RIGHT_HAND, 90, PROFILE)
    assert left_y < right_y


def test_vertical_scale_uses_cos_elevation():
    _, y = project_world((0, 0, 1), PROFILE)
    assert PROFILE.pivot.y - y == pytest.approx(160 * math.cos(math.radians(30)))


def test_ground_is_two_to_one_at_30_degrees():
    """Elevação 30° produz o losango 2:1 clássico."""
    _, y = project_world((0, 1, 0), PROFILE)
    x, _ = project_world((1, 0, 0), PROFILE)
    assert (x - PROFILE.pivot.x) / (PROFILE.pivot.y - y) == pytest.approx(2.0)


def test_camera_basis_is_orthonormal_right_handed():
    b = camera_basis(PROFILE)
    r, u, f = b.right, b.up, b.forward
    cross = (
        r[1] * u[2] - r[2] * u[1],
        r[2] * u[0] - r[0] * u[2],
        r[0] * u[1] - r[1] * u[0],
    )
    approx(cross, tuple(-c for c in f))
    assert b.ortho_scale == pytest.approx(2.0)


@pytest.mark.parametrize(
    ("east", "north", "name"),
    [
        (0, 1, "N"), (1, 1, "NE"), (1, 0, "E"), (1, -1, "SE"),
        (0, -1, "S"), (-1, -1, "SW"), (-1, 0, "W"), (-1, 1, "NW"),
        (0.1, 1, "N"), (-0.1, 1, "N"),
    ],
)
def test_vector_to_direction(east, north, name):
    assert vector_to_direction(east, north) == name


def test_vector_to_direction_rejects_zero():
    with pytest.raises(ValueError):
        vector_to_direction(0, 0)


def test_gltf_axes_match_spec():
    """glTF: +Y cima, +Z frente, -X direita (doc 17 §2)."""
    assert canonical_to_gltf((0, 0, 1)) == (0, 1, 0)
    assert canonical_to_gltf((0, 1, 0)) == (0, 0, 1)
    assert canonical_to_gltf((1, 0, 0)) == (-1, 0, 0)
