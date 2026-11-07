"""Contratos de dados versionados (doc 06). Fonte única de verdade dos schemas.

Todos os modelos usam ``extra="forbid"``: campo desconhecido é erro, não ruído
silencioso (SPEC-002). JSON Schema é gerado destes modelos por ``ics schemas``.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "1.0.0"
DIRECTION_ORDER: tuple[str, ...] = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")

Hex = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]
Slug = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_]{0,63}$")]
AssetId = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_]{0,63}$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    schema_version: str = SCHEMA_VERSION

    @field_validator("schema_version")
    @classmethod
    def _major_supported(cls, value: str) -> str:
        if not re.fullmatch(r"\d+\.\d+\.\d+", value):
            raise ValueError("schema_version deve ser semver")
        if value.split(".")[0] != SCHEMA_VERSION.split(".")[0]:
            raise ValueError(f"major de schema não suportado: {value}")
        return value


class Sub(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- CharacterSpec -----------------------------------------------------------
class BodyProfile(Sub):
    asset_id: AssetId
    scale: float = Field(1.0, gt=0.25, le=4.0)
    proportions: str = "chibi_moderate"


class Appearance(Sub):
    head_asset: AssetId
    hair_asset: AssetId | None = None
    skin_material: AssetId
    face_preset: AssetId


class Outfit(Sub):
    body_asset: AssetId
    accessories: list[AssetId] = Field(default_factory=list)
    weapon_asset: AssetId | None = None

    @field_validator("accessories")
    @classmethod
    def _unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("acessório duplicado")
        return value


class Palette(Sub):
    primary: Hex
    secondary: Hex
    accent: Hex


class CharacterSpec(Contract):
    id: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_]{0,63}$")]
    name: Annotated[str, Field(min_length=1, max_length=120)]
    slug: Slug
    family: Literal["humanoid"]
    seed: int = Field(default=0, ge=0, description="Variação procedural reproduzível (mesma seed = mesmo asset)")
    art_profile: AssetId
    body_profile: BodyProfile
    appearance: Appearance
    outfit: Outfit
    palette: Palette
    rig_profile: AssetId
    animation_profile: AssetId
    render_profile: AssetId
    revision: int = Field(1, ge=1)


# --- Biblioteca --------------------------------------------------------------
class AssetKind(StrEnum):
    BODY = "body"
    HEAD = "head"
    HAIR = "hair"
    FACE = "face"
    OUTFIT = "outfit"
    ACCESSORY = "accessory"
    WEAPON = "weapon"
    MATERIAL = "material"


class License(Sub):
    spdx_or_terms: str
    origin: str
    author: str
    redistribution_allowed: bool


class AssetMeta(Contract):
    """``asset.json`` de cada componente (doc 05 §4, RNF-010)."""

    id: AssetId
    version: str
    kind: AssetKind
    families: list[str]
    generator: str = Field(description="Função em blender/scripts/ics_blender/components.py")
    params: dict[str, Any] = Field(default_factory=dict)
    anchors: list[str] = Field(default_factory=list)
    depends_on: list[AssetId] = Field(default_factory=list)
    scale_reference_m: float = Field(1.0, gt=0)
    tags: list[str] = Field(default_factory=list)
    license: License


# --- Rig ---------------------------------------------------------------------
class Side(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    CENTER = "CENTER"
    NONE = "NONE"


class BoneSemantic(Sub):
    semantic_id: str
    blender_name: str
    side: Side
    role: str
    parent: str | None
    deform: bool
    head: tuple[float, float, float]
    tail: tuple[float, float, float]
    roll_deg: float = 0.0
    connected: bool = False
    required: bool = True


class SentinelPose(Sub):
    id: str
    bone: str
    mode: Literal["translate", "rotate"]
    vector: tuple[float, float, float]
    """Translação (m, armature) ou eixo-ângulo em graus (rotate)."""
    expected_moved: list[str]
    expected_static: list[str]


class RigProfile(Contract):
    id: AssetId
    version: str
    family: str
    reference_height_m: float = Field(gt=0)
    orientation: Literal["+Z_up,+Y_front,+X_right_anatomical"]
    max_influences: int = Field(4, ge=1, le=8)
    weight_sum_tolerance: float = Field(1e-3, gt=0)
    side_center_tolerance_m: float = Field(0.005, ge=0)
    compatible_animation_profiles: list[AssetId]
    ik_chains: dict[str, dict[str, str]] = Field(default_factory=dict)
    bones: list[BoneSemantic]
    sentinel_poses: list[SentinelPose]

    @model_validator(mode="after")
    def _semantics(self) -> RigProfile:
        ids = [b.semantic_id for b in self.bones]
        if len(ids) != len(set(ids)):
            raise ValueError("semantic_id duplicado")
        names = {b.blender_name for b in self.bones}
        if len(names) != len(self.bones):
            raise ValueError("blender_name duplicado")
        for bone in self.bones:
            if bone.parent is not None and bone.parent not in names:
                raise ValueError(f"pai inexistente: {bone.parent}")
        return self


# --- Animação ----------------------------------------------------------------
class ContactEvent(Sub):
    frame: int = Field(ge=0)
    event: Literal["LEFT_FOOT_CONTACT", "RIGHT_FOOT_CONTACT", "LEFT_SWING", "RIGHT_SWING"]


class AnimationTolerances(Sub):
    """Tolerâncias relativas à altura de referência do rig (unidade: fração de H)."""

    foot_slide_speed_h_per_s: float = Field(gt=0)
    ground_penetration_h: float = Field(gt=0)
    contact_height_h: float = Field(gt=0)
    ik_error_h: float = Field(gt=0)
    max_landmark_step_h: float = Field(gt=0)
    loop_landmark_gap_factor: float = Field(gt=0)
    """Maior salto último→primeiro permitido, como múltiplo do maior passo interno."""


class GaitParams(Sub):
    stride_m: float = Field(ge=0)
    stance_fraction: float = Field(gt=0, le=1)
    foot_lift_m: float = Field(ge=0)
    pelvis_drop_m: float = Field(ge=0)
    pelvis_bob_m: float = Field(ge=0)
    arm_swing_deg: float = Field(ge=0)
    forearm_bend_deg: float = Field(ge=0)
    torso_lean_deg: float = 0
    torso_twist_deg: float = 0


class AnimationClip(Sub):
    animation_id: Literal["idle", "walk", "run"]
    version: str
    fps: int = Field(gt=0, le=60)
    frame_count: int = Field(gt=1, le=64)
    loop: bool
    root_motion: Literal["in_place"]
    ground_speed_mps: float = Field(ge=0, description="Derivada/validada: velocidade de esteira")
    gait: GaitParams
    events: list[ContactEvent]
    tolerances: AnimationTolerances
    approval: Literal["UNAPPROVED", "APPROVED"] = "UNAPPROVED"

    @property
    def duration_s(self) -> float:
        return self.frame_count / self.fps

    @model_validator(mode="after")
    def _events_in_range(self) -> AnimationClip:
        for event in self.events:
            if event.frame >= self.frame_count:
                raise ValueError(f"evento fora do clip: {event}")
        return self


class AnimationProfile(Contract):
    id: AssetId
    version: str
    rig_profile: AssetId
    clips: list[AnimationClip]

    @field_validator("clips")
    @classmethod
    def _unique_clips(cls, clips: list[AnimationClip]) -> list[AnimationClip]:
        ids = [c.animation_id for c in clips]
        if len(ids) != len(set(ids)):
            raise ValueError("clip duplicado")
        return clips


# --- Render ------------------------------------------------------------------
class Pixel(Sub):
    x: float
    y: float


class Canvas(Sub):
    width: int = Field(ge=16, le=2048)
    height: int = Field(ge=16, le=2048)


class RenderProfile(Contract):
    id: AssetId
    version: str
    projection: Literal["orthographic"]
    elevation_deg: float = Field(gt=0, lt=90)
    azimuth_deg: float = 0.0
    canvas: Canvas
    pixels_per_meter: float = Field(gt=0)
    pivot: Pixel
    safety_margin_px: int = Field(ge=0)
    transparent: Literal[True] = True
    engine: Literal["BLENDER_EEVEE"]
    samples: int = Field(ge=1, le=512)
    filter_width_px: float = Field(1.5, gt=0)
    view_transform: Literal["Standard"] = "Standard"
    rotation_strategy: Literal["rotate_character_root"]
    direction_order: list[str]
    headings_deg: dict[str, float]

    @model_validator(mode="after")
    def _directions(self) -> RenderProfile:
        if tuple(self.direction_order) != DIRECTION_ORDER:
            raise ValueError("ordem canônica de direções violada")
        if set(self.headings_deg) != set(DIRECTION_ORDER):
            raise ValueError("headings_deg deve mapear exatamente as oito direções")
        base = self.headings_deg["N"]
        for index, name in enumerate(DIRECTION_ORDER):
            expected = (base + index * 45.0) % 360.0
            if abs((self.headings_deg[name] - expected + 180) % 360 - 180) > 1e-6:
                raise ValueError(f"heading de {name} não é N + {index}×45° horário")
        return self


class Light(Sub):
    name: str
    azimuth_deg: float
    elevation_deg: float
    energy: float = Field(gt=0)
    color: Hex
    angle_deg: float = Field(10.0, ge=0)


class PixelMaterialRole(Contract):
    """Como um material vira pixels: rampa de tons, matiz, brilho, padrão e contorno."""

    base: Hex | None = Field(default=None, description="Vazio = cor da própria peça (paleta do personagem)")
    tones: int = Field(ge=1, le=6, description="Tons de luz e sombra, sem contar o brilho")
    value_range: tuple[float, float] = Field(default=(.55, 1.0), description="Brilho do tom mais escuro e do mais claro")
    shadow_hue_shift_deg: float = Field(default=12.0, description="Giro de matiz nas sombras, rumo ao frio")
    highlight: Hex | None = Field(default=None, description="Tom de brilho especular; vazio = sem brilho")
    highlight_threshold: float = Field(default=.92, ge=0, le=1)
    ao_strength: float = Field(default=.5, ge=0, le=1)
    pattern: str | None = Field(default=None, description="none, stitch, weave, grain, glyph")
    pattern_scale: float = Field(default=40.0, gt=0)
    emissive: bool = False
    shading: bool = Field(default=True, description="Falso = cor chapada (olhos, boca)")
    protect: bool = Field(default=False, description="Não sofre limpeza de pixels órfãos")
    outline: Hex | None = Field(default=None, description="Vazio = tom mais escuro escurecido (contorno seletivo)")


class PixelArtSettings(Contract):
    reference_canvas_px: int = Field(gt=0, description="Resolução de referência do quadro")
    light_bands: list[float] = Field(description="Limiares de luz entre tons, do escuro ao claro")
    roles: dict[str, PixelMaterialRole]
    part_roles: dict[str, str] = Field(description="Nome ou prefixo da peça → papel; '*' = padrão")
    outline_mode: str = Field(default="outside", description="outside soma 1 px fora; inside pinta a borda")
    outline_ink: Hex = Field(default="#1B1424", description="Tinta misturada ao contorno")
    outline_ink_mix: float = Field(default=.55, ge=0, le=1)
    lit_outline_mix: float = Field(default=.2, ge=0, le=1, description="Mistura no lado iluminado (sel-out)")
    internal_line_depth_m: float = Field(default=.05, gt=0, description="Salto de profundidade que vira linha interna")
    cluster_min_px: int = Field(default=2, ge=1, description="Ilhas menores viram o tom vizinho")
    glow_radius_px: int = Field(default=1, ge=0)
    alpha: str = Field(default="binary", description="binary: só 0 ou 255; sem semitransparência")
    max_colors: int = Field(default=48, gt=0)


MaterialRole = PixelMaterialRole  # papel de material comum a todos os acabamentos


class SmoothArtSettings(Contract):
    """Ilustração suave: mesmos passes do pixel art, composição contínua com antialiasing real."""

    reference_canvas_px: int = Field(gt=0)
    supersample: int = Field(default=3, ge=1, le=6, description="Passes em N× a resolução final, reduzidos por média")
    light_bands: list[float] = Field(description="Centros das transições entre tons")
    band_softness: float = Field(default=.06, ge=0, le=.5, description="Meia-largura da transição suave entre tons")
    roles: dict[str, MaterialRole]
    part_roles: dict[str, str]
    texture_strength: float = Field(default=.35, ge=0, le=1, description="Quanto o padrão escurece, em fração de um tom")
    outline_px: float = Field(default=2.0, ge=0, description="Contorno externo no tamanho final")
    outline_shadow_extra_px: float = Field(default=1.0, ge=0, description="Peso extra no lado oposto à luz")
    shadow_side: tuple[float, float] = Field(default=(.6, .8), description="Direção de tela (x, y) do lado da sombra")
    outline_ink: Hex = "#2A1E2E"
    outline_ink_mix: float = Field(default=.55, ge=0, le=1)
    internal_line_px: float = Field(default=1.0, ge=0)
    internal_line_depth_m: float = Field(default=.07, gt=0)
    internal_line_strength: float = Field(default=.8, ge=0, le=1)
    glow_radius_px: float = Field(default=4.0, ge=0)
    glow_strength: float = Field(default=.6, ge=0, le=1)
    noise_strength: float = Field(default=0.0, ge=0, le=1, description="Variação contínua de tom pelo ruído, em tons")
    rim_px: float = Field(default=0.0, ge=0, description="Largura da luz de borda no lado iluminado")
    rim_strength: float = Field(default=0.0, ge=0, le=1)
    rim_color: Hex = "#FFF4DC"


class ArtProfile(Contract):
    id: AssetId
    version: str
    reference_height_m: float = Field(gt=0)
    lights: list[Light]
    world_color: Hex
    world_strength: float = Field(ge=0)
    toon_steps: list[tuple[float, float]] = Field(
        description="(posição no ramp, multiplicador de brilho)"
    )
    light_shadows: bool = True
    outline_thickness_m: float = Field(ge=0)
    outline_darken: float = Field(gt=0, le=1)
    allowed_references: list[str] = Field(default_factory=list)
    pixel: PixelArtSettings | None = Field(
        default=None, description="Presente = acabamento pixel art montado a partir de passes nativos"
    )
    smooth: SmoothArtSettings | None = Field(
        default=None, description="Presente = ilustração suave montada a partir dos mesmos passes"
    )


class ProportionProfile(Contract):
    """Proporção canônica do personagem (D2). Medidas em metros, sem cabelo nem calçado."""

    id: AssetId
    version: str
    family: str
    heads_tall: float = Field(gt=0)
    height_m: float = Field(gt=0)
    head_height_m: float = Field(gt=0)
    chin_z_m: float = Field(gt=0)
    shoulder_half_width_m: float = Field(gt=0)
    hip_z_m: float = Field(gt=0)
    knee_z_m: float = Field(gt=0)
    ankle_z_m: float = Field(gt=0)
    hand_length_m: float = Field(gt=0)
    foot_length_m: float = Field(gt=0)
    tolerance_heads: float = Field(gt=0)
    notes: str = ""

    @model_validator(mode="after")
    def _coherent(self) -> ProportionProfile:
        if abs(self.height_m / self.head_height_m - self.heads_tall) > self.tolerance_heads:
            raise ValueError("altura/cabeça incoerente com heads_tall")
        if abs(self.height_m - self.head_height_m - self.chin_z_m) > 1e-3:
            raise ValueError("queixo incoerente com altura e cabeça")
        if not self.ankle_z_m < self.knee_z_m < self.hip_z_m < self.chin_z_m:
            raise ValueError("articulações fora de ordem")
        return self


# --- Manifests ---------------------------------------------------------------
class ComponentUse(Sub):
    asset_id: str
    version: str
    kind: str
    anchor: str | None = None
    meta_sha256: str


class BuildManifest(Contract):
    character_id: str
    spec_sha256: str
    builder_version: str
    blender_version: str
    source_scene: str
    source_scene_sha256: str
    components: list[ComponentUse]
    materials: list[str]
    objects: list[dict[str, Any]]
    warnings: list[str] = Field(default_factory=list)


class ExportedFile(Sub):
    path: str
    sha256: str
    bytes: int = Field(gt=0)


class FrameRect(Sub):
    index: int = Field(ge=0)
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(gt=0)
    h: int = Field(gt=0)


class DirectionAtlas(Sub):
    file: str
    atlas_width: int
    atlas_height: int
    frame_width: int
    frame_height: int
    frame_count: int
    gutter_px: int
    heading_deg: float
    pivot: Pixel
    frames: list[FrameRect]


class AnimationExport(Sub):
    animation: str
    fps: int
    loop: bool
    frame_count: int
    duration_s: float
    ground_speed_mps: float
    events: list[ContactEvent]
    direction_order: list[str]
    directions: dict[str, DirectionAtlas]


class ReleaseStatus(StrEnum):
    EXPERIMENTAL = "experimental"
    REVIEW = "review"
    PRODUCTION = "production"


class ExportManifest(Contract):
    character_id: str
    character_name: str
    character_revision: int
    art_profile: str
    render_profile: str
    rig_profile: str
    animation_profile: str
    release: ReleaseStatus
    approval: Literal["UNAPPROVED", "APPROVED"]
    exporter_version: str
    blender_version: str
    target: str
    tested_compatibility: str | None
    created_at: datetime
    direction_order: list[str]
    animations: list[AnimationExport]
    files: list[ExportedFile]

    @model_validator(mode="after")
    def _production_needs_approval(self) -> ExportManifest:
        if self.release is ReleaseStatus.PRODUCTION and self.approval != "APPROVED":
            raise ValueError("production exige aprovação registrada")
        return self


# --- Jobs e gates ------------------------------------------------------------
class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING_REVIEW = "WAITING_REVIEW"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Stage(StrEnum):
    SPEC_VALIDATION = "SPEC_VALIDATION"
    BUILD = "BUILD"
    RIG = "RIG"
    ANIMATION = "ANIMATION"
    RENDER = "RENDER"
    POST_PROCESS = "POST_PROCESS"
    VALIDATION = "VALIDATION"
    EXPORT = "EXPORT"
    RUNTIME = "RUNTIME"


def utcnow() -> datetime:
    return datetime.now(UTC)


class GenerationJob(Contract):
    id: str
    project_id: str
    character_id: str
    type: str
    status: JobStatus = JobStatus.QUEUED
    current_stage: Stage | None = None
    progress: float | None = Field(None, ge=0, le=1)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    input_manifest: str
    output_dir: str
    error: str | None = None


class GateStatus(StrEnum):
    PENDING = "PENDING"
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_TESTED = "NOT_TESTED"


class CheckResult(Sub):
    """Linha da matriz de testes (doc 23 §4)."""

    id: str
    status: GateStatus
    detail: str = ""
    tolerance: str | None = None
    evidence: list[str] = Field(default_factory=list)


class GateReport(Contract):
    gate: str
    status: GateStatus
    checks: list[CheckResult]

    @classmethod
    def from_checks(cls, gate: str, checks: list[CheckResult]) -> GateReport:
        return cls(gate=gate, status=aggregate(checks), checks=checks)


def aggregate(checks: list[CheckResult]) -> GateStatus:
    """Pior status vence; NOT_TESTED nunca vira PASS (doc 16 §6, doc 20 §4)."""
    order = [
        GateStatus.FAIL,
        GateStatus.REJECTED,
        GateStatus.NOT_TESTED,
        GateStatus.PENDING,
        GateStatus.REVIEW,
        GateStatus.WARN,
        GateStatus.APPROVED,
        GateStatus.PASS,
    ]
    if not checks:
        return GateStatus.NOT_TESTED
    present = {check.status for check in checks}
    return next(status for status in order if status in present)


ALL_CONTRACTS: dict[str, type[Contract]] = {
    "character_spec": CharacterSpec,
    "asset_meta": AssetMeta,
    "rig_profile": RigProfile,
    "animation_profile": AnimationProfile,
    "render_profile": RenderProfile,
    "art_profile": ArtProfile,
    "proportion_profile": ProportionProfile,
    "build_manifest": BuildManifest,
    "export_manifest": ExportManifest,
    "generation_job": GenerationJob,
    "gate_report": GateReport,
}
