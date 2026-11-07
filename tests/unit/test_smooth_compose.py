"""Compositor de ilustração suave: regras verificadas com passes sintéticos (sem Blender)."""

import numpy as np

from app.schemas.contracts import MaterialRole, SmoothArtSettings
from engines.postprocess_engine.pixel import Passes
from engines.postprocess_engine.smooth import compose_smooth


def settings(**extra):
    data = {"reference_canvas_px": 32, "supersample": 3, "light_bands": [.2, .45, .7],
            "roles": {"cloth": MaterialRole(tones=4, value_range=(.5, 1.0))}, "part_roles": {"*": "cloth"},
            "outline_px": 1.5, "outline_shadow_extra_px": 1.0, "shadow_side": (1.0, 0.0), "glow_radius_px": 0}
    data.update(extra)
    return SmoothArtSettings(**data)


def disc(size=96, radius=30, light=None):
    y, x = np.mgrid[0:size, 0:size]
    ids = ((x - size / 2) ** 2 + (y - size / 2) ** 2 <= radius ** 2).astype(int)
    lit = np.clip(.5 - (x - size / 2) / (2.2 * radius), 0, 1) if light is None else np.full((size, size), light)
    return Passes(ids=ids, light=lit * .5, ao=np.ones((size, size)), pattern=np.zeros((size, size), bool),
                  depth=np.full((size, size), 5.0))


PARTS = [{"index": 1, "name": "tunic", "color": "#5C72AE"}]


def test_output_is_downsampled_with_real_antialiasing():
    image = np.asarray(compose_smooth(disc(), PARTS, settings()))
    assert image.shape == (32, 32, 4)
    partial = (image[..., 3] > 0) & (image[..., 3] < 255)
    assert partial.sum() > 10  # borda suave, não serrilhada
    assert (image[image[..., 3] == 0][:, :3] == 0).all()


def test_shading_is_continuous_not_stepped():
    image = np.asarray(compose_smooth(disc(), PARTS, settings())).astype(int)
    row = image[16, 8:24, :3].sum(axis=1)
    assert len(set(row.tolist())) > 6  # mais valores que os 4 tons: transições suaves


def test_outline_is_heavier_on_shadow_side():
    image = np.asarray(compose_smooth(disc(light=.4), PARTS, settings()))
    coverage = image[..., 3].astype(float).sum(axis=0)  # alpha somado por coluna
    left, right = coverage[:16].sum(), coverage[16:].sum()
    assert right > left  # sombra à direita (+x): contorno mais grosso desse lado


def test_edge_has_no_light_fringe():
    image = np.asarray(compose_smooth(disc(light=.5), PARTS, settings())).astype(int)
    edge = (image[..., 3] > 0) & (image[..., 3] < 255)
    interior = image[..., 3] == 255
    assert image[edge][:, :3].sum(axis=1).max() <= image[interior][:, :3].sum(axis=1).max()
