"""Compositor de pixel art: regras verificadas com passes sintéticos (sem Blender)."""

import numpy as np

from app.schemas.contracts import PixelArtSettings, PixelMaterialRole
from engines.postprocess_engine.pixel import Passes, compose, hex_rgb, ramp, role_of


def settings(**extra):
    roles = {
        "cloth": PixelMaterialRole(tones=4, value_range=(.4, 1.0)),
        "eyes": PixelMaterialRole(tones=1, shading=False, protect=True),
        "gem": PixelMaterialRole(tones=3, emissive=True, protect=True),
    }
    data = {"reference_canvas_px": 32, "light_bands": [.2, .45, .7], "roles": roles,
            "part_roles": {"*": "cloth", "eyes": "eyes", "orb": "gem"}, "glow_radius_px": 0}
    data.update(extra)
    return PixelArtSettings(**data)


def square(size=32, lo=8, hi=24, light=.4):
    ids = np.zeros((size, size), int)
    ids[lo:hi, lo:hi] = 1
    return Passes(ids=ids, light=np.full((size, size), light), ao=np.ones((size, size)),
                  pattern=np.zeros((size, size), bool), depth=np.full((size, size), 5.0))


PARTS = [{"index": 1, "name": "tunic", "color": "#5C72AE"}, {"index": 2, "name": "eyes", "color": "#202020"}]


def test_alpha_is_binary_and_outline_is_outside():
    image = np.asarray(compose(square(), PARTS, settings()))
    assert set(np.unique(image[..., 3])) == {0, 255}
    # 16×16 de peça + 1 px de contorno em volta (sem cantos: vizinhança em cruz).
    assert (image[..., 3] > 0).sum() == 16 * 16 + 4 * 16
    assert image[7, 8, 3] == 255 and image[7, 7, 3] == 0
    assert (image[image[..., 3] == 0][:, :3] == 0).all()


def test_shadow_tones_shift_hue_and_get_darker():
    tones = ramp(hex_rgb("#5C72AE"), PixelMaterialRole(tones=4, value_range=(.4, 1.0), shadow_hue_shift_deg=16))
    assert tones[0].sum() < tones[-1].sum()
    assert not np.allclose(tones[0] / tones[0].sum(), tones[-1] / tones[-1].sum(), atol=.01)


def test_internal_line_only_on_depth_jump_between_parts():
    p = square()
    p.ids[8:24, 16:24] = 2  # outra peça atrás
    p.depth[8:24, 16:24] = 5.5
    parts = [PARTS[0], {"index": 2, "name": "cape", "color": "#5C72AE"}]
    image = np.asarray(compose(p, parts, settings(internal_line_depth_m=.1))).astype(int)
    assert image[12, 16, :3].sum() < image[12, 20, :3].sum()  # coluna junto ao salto escureceu
    flat = np.asarray(compose(square(), PARTS, settings())).astype(int)
    assert len({tuple(c) for c in flat[10:22, 10:22, :3].reshape(-1, 3)}) == 1


def test_orphan_pixel_is_cleaned_but_protected_material_is_kept():
    p = square()
    p.light[15, 15] = .05  # um pixel isolado de sombra
    image = np.asarray(compose(p, PARTS, settings(cluster_min_px=2))).astype(int)
    assert (image[15, 15, :3] == image[14, 15, :3]).all()
    p.ids[15, 15] = 2  # o mesmo pixel como olho: protegido
    image = np.asarray(compose(p, PARTS, settings(cluster_min_px=2))).astype(int)
    assert not (image[15, 15, :3] == image[14, 15, :3]).all()


def test_role_lookup_uses_longest_prefix():
    table = {"*": "x", "boot_": "leather", "boot_sole_": "sole"}
    assert role_of("boot_sole_l", table) == "sole"
    assert role_of("boot_l", table) == "leather"
    assert role_of("hood", table) == "x"


def test_trimmed_atlas_rebuilds_full_frame(tmp_path):
    from PIL import Image

    from app.schemas.contracts import RenderProfile
    from engines.postprocess_engine.atlas import build_atlas, check_atlas

    data = {"schema_version": "1.0.0", "id": "t", "version": "1", "projection": "orthographic", "elevation_deg": 30,
            "azimuth_deg": 0, "canvas": {"width": 32, "height": 32}, "pixels_per_meter": 20, "pivot": {"x": 16, "y": 28},
            "safety_margin_px": 1, "engine": "BLENDER_EEVEE", "samples": 1, "rotation_strategy": "rotate_character_root",
            "direction_order": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
            "headings_deg": {d: i * 45 for i, d in enumerate(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])},
            "atlas_trim": True}
    render = RenderProfile(**data)
    frames = []
    for i in range(3):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        img.paste((200, 50, 50, 255), (8 + i, 10, 20 + i, 26))
        frames.append(tmp_path / f"f{i}.png")
        img.save(frames[-1])
    atlas = build_atlas(frames, tmp_path / "walk_S.png", render, 180)
    assert atlas.frames[0].w < 32 and atlas.frames[0].ox > 0
    assert check_atlas(tmp_path / "walk_S.png", atlas, frames) == []
