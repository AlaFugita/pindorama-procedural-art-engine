"""Resolve CharacterSpec + biblioteca em um payload concreto (gate G1, CA-001).

Ausência ou incompatibilidade é detectada aqui, antes de abrir o Blender.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import LIBRARY_DIR, read_json, sha256_file
from app.domain.directions import camera_basis
from app.schemas.contracts import (
    AnimationProfile,
    ArtProfile,
    AssetKind,
    AssetMeta,
    CharacterSpec,
    CheckResult,
    ComponentUse,
    GateStatus,
    RenderProfile,
    RigProfile,
)


class SpecResolutionError(ValueError):
    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


class Library:
    def __init__(self, root: Path = LIBRARY_DIR):
        self.root = root
        self.assets: dict[str, AssetMeta] = {}
        self.paths: dict[str, Path] = {}
        for folder in ("components", "materials"):
            for path in sorted((root / folder).glob("*/asset.json")):
                meta = AssetMeta.model_validate(read_json(path))
                if meta.id in self.assets:
                    raise ValueError(f"asset duplicado: {meta.id}")
                if meta.id != path.parent.name:
                    raise ValueError(f"id difere da pasta: {path}")
                self.assets[meta.id] = meta
                self.paths[meta.id] = path

    def list(self, kind: AssetKind | None = None, family: str | None = None) -> list[AssetMeta]:
        return [
            a for a in self.assets.values()
            if (kind is None or a.kind == kind) and (family is None or family in a.families)
        ]

    def rig(self, rig_id: str) -> RigProfile:
        return RigProfile.model_validate(read_json(self.root / "rigs" / rig_id / "rig.json"))

    def animation(self, profile_id: str) -> AnimationProfile:
        return AnimationProfile.model_validate(
            read_json(self.root / "animations" / f"{profile_id}.json")
        )

    def render(self, profile_id: str) -> RenderProfile:
        return RenderProfile.model_validate(
            read_json(self.root / "profiles" / "render" / f"{profile_id}.json")
        )

    def art(self, profile_id: str) -> ArtProfile:
        return ArtProfile.model_validate(
            read_json(self.root / "profiles" / "art" / f"{profile_id}.json")
        )


@dataclass
class Resolved:
    spec: CharacterSpec
    rig: RigProfile
    animation: AnimationProfile
    render: RenderProfile
    art: ArtProfile
    components: list[AssetMeta]
    uses: list[ComponentUse]
    skin_color: str

    def render_payload(self) -> dict[str, Any]:
        basis = camera_basis(self.render)
        return {
            **self.render.model_dump(mode="json"),
            "camera": {"matrix_world": basis.matrix_world(), "ortho_scale": basis.ortho_scale},
        }

    def build_payload(self, blend_path: Path) -> dict[str, Any]:
        return {
            "character": self.spec.model_dump(mode="json"),
            "rig": self.rig.model_dump(mode="json"),
            "art": self.art.model_dump(mode="json"),
            "render": self.render_payload(),
            "components": [c.model_dump(mode="json") for c in self.components],
            "skin_color": self.skin_color,
            "hair_color": self.spec.palette.secondary,
            "blend_path": str(blend_path),
        }


def resolve(spec: CharacterSpec, library: Library) -> Resolved:
    problems: list[str] = []

    def need(asset_id: str, kind: AssetKind) -> AssetMeta | None:
        meta = library.assets.get(asset_id)
        if meta is None:
            problems.append(f"asset ausente: {asset_id}")
            return None
        if meta.kind != kind:
            problems.append(f"{asset_id}: tipo {meta.kind}, esperado {kind}")
        if spec.family not in meta.families:
            problems.append(f"{asset_id}: incompatível com a família {spec.family}")
        return meta

    wanted: list[tuple[str, AssetKind]] = [
        (spec.body_profile.asset_id, AssetKind.BODY),
        (spec.appearance.head_asset, AssetKind.HEAD),
        (spec.appearance.face_preset, AssetKind.FACE),
        (spec.outfit.body_asset, AssetKind.OUTFIT),
    ]
    if spec.appearance.hair_asset:
        wanted.append((spec.appearance.hair_asset, AssetKind.HAIR))
    wanted += [(a, AssetKind.ACCESSORY) for a in spec.outfit.accessories]
    if spec.outfit.weapon_asset:
        wanted.append((spec.outfit.weapon_asset, AssetKind.WEAPON))
    components = [m for a, k in wanted if (m := need(a, k)) is not None]
    skin = need(spec.appearance.skin_material, AssetKind.MATERIAL)

    if spec.body_profile.scale != 1.0:
        problems.append("escala de corpo diferente de 1.0 ainda não é suportada pelo rig/animação")

    def profile(loader, name: str, label: str):
        try:
            return loader(name)
        except FileNotFoundError:
            problems.append(f"{label} ausente: {name}")
            return None

    rig = profile(library.rig, spec.rig_profile, "RigProfile")
    animation = profile(library.animation, spec.animation_profile, "AnimationProfile")
    render = profile(library.render, spec.render_profile, "RenderProfile")
    art = profile(library.art, spec.art_profile, "ArtProfile")

    if rig is not None:
        if rig.family != spec.family:
            problems.append(f"rig {rig.id} não é da família {spec.family}")
        if animation is not None and animation.id not in rig.compatible_animation_profiles:
            problems.append(f"animação {animation.id} incompatível com o rig {rig.id}")
    if animation is not None and animation.rig_profile != spec.rig_profile:
        problems.append(f"animação {animation.id} exige o rig {animation.rig_profile}")

    if problems:
        raise SpecResolutionError(problems)

    uses = [
        ComponentUse(
            asset_id=m.id, version=m.version, kind=m.kind.value,
            anchor=m.anchors[0] if m.anchors else None,
            meta_sha256=sha256_file(library.paths[m.id]),
        )
        for m in [*components, skin]
    ]
    return Resolved(
        spec, rig, animation, render, art, components, uses, skin.params["base"]
    )


def gate_g1_checks(spec_data: dict[str, Any], library: Library) -> tuple[Resolved | None, list[CheckResult]]:
    try:
        spec = CharacterSpec.model_validate(spec_data)
    except ValueError as error:
        return None, [CheckResult(id="SPEC-001", status=GateStatus.FAIL, detail=str(error))]
    checks = [CheckResult(id="SPEC-001", status=GateStatus.PASS, detail="schema válido")]
    try:
        resolved = resolve(spec, library)
    except SpecResolutionError as error:
        checks.append(CheckResult(id="SPEC-003", status=GateStatus.FAIL, detail=str(error)))
        return None, checks
    checks.append(CheckResult(
        id="SPEC-003", status=GateStatus.PASS,
        detail=f"{len(resolved.uses)} componentes e 4 perfis resolvidos",
    ))
    return resolved, checks
