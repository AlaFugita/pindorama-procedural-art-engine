"""Rosto decalcado: projeção, visibilidade e máscara pela cabeça (sem Blender)."""

import numpy as np

from engines.postprocess_engine.pixel import Passes
from engines.postprocess_engine.smooth import apply_face_decal


def scene(normal):
    ids = np.zeros((40, 40), int)
    ids[5:35, 5:35] = 1
    ids[5:12, 5:35] = 2  # outra peça na frente (capuz) cobre o topo
    p = Passes(ids=ids, light=np.zeros((40, 40)), ao=np.ones((40, 40)), pattern=np.zeros((40, 40), bool),
               depth=np.full((40, 40), 5.0))
    square = [(-.3, 0, -.3), (.3, 0, -.3), (.3, 0, .6), (-.3, 0, .6)]
    decal = {"camera": np.eye(4).tolist(), "ortho_scale": 2.0,
             "features": [{"name": "eye", "color": "#000000", "alpha": 1.0, "loop": square, "normal": normal}]}
    return p, decal


PARTS = [{"index": 1, "name": "head"}, {"index": 2, "name": "hood"}]


def test_decal_paints_only_visible_head_pixels():
    p, decal = scene([0, 0, 1])
    rgb = np.full((40, 40, 3), 200.0)
    apply_face_decal(rgb, p, PARTS, decal, np.eye(4).tolist())
    painted = rgb.sum(axis=-1) < 300
    assert painted[20, 20]  # centro do rosto
    assert not painted[8, 20]  # coberto pela outra peça
    assert not painted[2, 20]  # fora da cabeça


def test_decal_facing_away_is_hidden():
    p, decal = scene([0, 0, -1])
    rgb = np.full((40, 40, 3), 200.0)
    apply_face_decal(rgb, p, PARTS, decal, np.eye(4).tolist())
    assert (rgb == 200.0).all()


def test_blink_swaps_open_eye_for_closed_stroke():
    p, decal = scene([0, 0, 1])
    closed = dict(decal["features"][0], name="closed_1", color="#FF0000")
    decal["features"] = [dict(decal["features"][0], name="eye_1"), closed]
    open_rgb = np.full((40, 40, 3), 200.0)
    apply_face_decal(open_rgb, p, PARTS, decal, np.eye(4).tolist(), blink=False)
    blink_rgb = np.full((40, 40, 3), 200.0)
    apply_face_decal(blink_rgb, p, PARTS, decal, np.eye(4).tolist(), blink=True)
    assert open_rgb[20, 20, 0] < 50 and blink_rgb[20, 20, 0] > 200
