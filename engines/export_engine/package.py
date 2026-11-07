"""Pacote final e manifesto (doc 09). Falha de validação nunca toca exportação anterior."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import read_json, sha256_file, write_json
from app.schemas.contracts import (
    DIRECTION_ORDER,
    AnimationExport,
    AnimationProfile,
    CharacterSpec,
    CheckResult,
    DirectionAtlas,
    ExportedFile,
    ExportManifest,
    GateStatus,
    ReleaseStatus,
    RenderProfile,
)

EXPORTER_VERSION = "0.1.0"


def _file_entries(root: Path) -> list[ExportedFile]:
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append(ExportedFile(
                path=path.relative_to(root).as_posix(), sha256=sha256_file(path),
                bytes=path.stat().st_size,
            ))
    return entries


def verify_manifest(root: Path) -> list[str]:
    """EXP-001/EXP-002: tudo listado existe, confere e nada fica fora da lista."""
    problems: list[str] = []
    manifest = ExportManifest.model_validate(read_json(root / "manifest.json"))
    listed = {entry.path: entry for entry in manifest.files}
    actual = {
        p.relative_to(root).as_posix() for p in root.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }
    for missing in sorted(set(listed) - actual):
        problems.append(f"listado e ausente: {missing}")
    for extra in sorted(actual - set(listed)):
        problems.append(f"presente e não listado: {extra}")
    for name in sorted(set(listed) & actual):
        path = root / name
        if sha256_file(path) != listed[name].sha256:
            problems.append(f"hash divergente: {name}")
        if path.stat().st_size != listed[name].bytes:
            problems.append(f"tamanho divergente: {name}")
    for animation in manifest.animations:
        if animation.direction_order != list(DIRECTION_ORDER):
            problems.append(f"{animation.animation}: ordem de direções inválida")
        if set(animation.directions) != set(DIRECTION_ORDER):
            problems.append(f"{animation.animation}: direções incompletas")
        for direction, atlas in animation.directions.items():
            if f"atlases/{atlas.file}" not in listed:
                problems.append(f"{animation.animation}/{direction}: atlas não listado")
            if atlas.frame_count != animation.frame_count:
                problems.append(f"{animation.animation}/{direction}: frame_count divergente")
    return problems


def release_for(checks: list[CheckResult], approved: bool) -> ReleaseStatus:
    statuses = {c.status for c in checks}
    if statuses & {GateStatus.FAIL, GateStatus.REJECTED, GateStatus.NOT_TESTED, GateStatus.PENDING}:
        return ReleaseStatus.EXPERIMENTAL
    return ReleaseStatus.PRODUCTION if approved else ReleaseStatus.REVIEW


def stage_export(
    staging: Path,
    spec: CharacterSpec,
    render: RenderProfile,
    animation: AnimationProfile,
    atlases: dict[str, dict[str, DirectionAtlas]],
    atlas_dir: Path,
    blend: Path,
    extras: dict[str, Path],
    blender_version: str,
    release: ReleaseStatus,
    approved: bool,
) -> Path:
    """Monta o pacote em ``staging`` (área do job). A publicação é separada."""
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "atlases").mkdir(parents=True)
    (staging / "source").mkdir()
    (staging / "metadata").mkdir()
    (staging / "qa").mkdir()
    write_json(staging / "character.json", spec.model_dump(mode="json"))
    shutil.copy2(blend, staging / "source" / "character.blend")
    animations = []
    for clip in animation.clips:
        cid = clip.animation_id
        for atlas in atlases[cid].values():
            shutil.copy2(atlas_dir / atlas.file, staging / "atlases" / atlas.file)
        animations.append(AnimationExport(
            animation=cid, fps=clip.fps, loop=clip.loop, frame_count=clip.frame_count,
            duration_s=clip.duration_s, ground_speed_mps=clip.ground_speed_mps,
            events=clip.events, direction_order=list(DIRECTION_ORDER), directions=atlases[cid],
        ))
    for name, path in extras.items():
        target = staging / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    write_json(staging / "metadata" / "animations.json", {
        "schema_version": "1.0.0", "character_id": spec.id,
        "animations": [a.model_dump(mode="json") for a in animations],
    })
    write_json(staging / "metadata" / "directions.json", {
        "schema_version": "1.0.0", "direction_order": list(DIRECTION_ORDER),
        "headings_deg": render.headings_deg,
        "convention": "heading horário a partir do norte do mapa; câmera fixa ao sul",
    })
    manifest = ExportManifest(
        character_id=spec.id, character_name=spec.name, character_revision=spec.revision,
        art_profile=spec.art_profile, render_profile=spec.render_profile,
        rig_profile=spec.rig_profile, animation_profile=spec.animation_profile,
        release=release, approval="APPROVED" if approved else "UNAPPROVED",
        exporter_version=EXPORTER_VERSION, blender_version=blender_version, target="godot4",
        tested_compatibility=None, created_at=datetime.now(UTC),
        direction_order=list(DIRECTION_ORDER), animations=animations,
        files=_file_entries(staging),
    )
    write_json(staging / "manifest.json", manifest.model_dump(mode="json"))
    return staging


def stamp_runtime(staging: Path, version: str, release: ReleaseStatus) -> None:
    """Registra a compatibilidade testada depois do teste real no Godot."""
    data: dict[str, Any] = read_json(staging / "manifest.json")
    data["tested_compatibility"] = version
    data["release"] = release.value
    write_json(staging / "manifest.json", ExportManifest.model_validate(data).model_dump(mode="json"))


def publish(staging: Path, destination: Path) -> Path:
    """Troca atômica; a versão anterior fica em ``.previous`` até a nova estar no lugar."""
    problems = verify_manifest(staging)
    if problems:
        raise RuntimeError("; ".join(problems[:5]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".incoming")
    previous = destination.with_name(destination.name + ".previous")
    if temp.exists():
        shutil.rmtree(temp)
    shutil.copytree(staging, temp)
    if previous.exists():
        shutil.rmtree(previous)
    if destination.exists():
        destination.replace(previous)
    temp.replace(destination)
    return destination
