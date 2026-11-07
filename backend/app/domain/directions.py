"""DirectionConvention e projeção — único lugar com matemática de orientação (doc 17 §2–3).

Coordenadas canônicas do personagem: destro, +Z cima, +Y frente, +X direita anatômica.
Mundo de render: +Y = norte do mapa, +X = leste, câmera fixa ao sul olhando para o norte.
Heading é medido em graus no sentido horário a partir do norte. Girar o root em heading
``h`` equivale a rotação de ``-h`` em torno de +Z.

A conversão para glTF também mora aqui (``canonical_to_gltf``), para não espalhar eixos.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from app.schemas.contracts import DIRECTION_ORDER, RenderProfile

Vec3 = tuple[float, float, float]


def direction_index(name: str) -> int:
    return DIRECTION_ORDER.index(name)


def heading_to_forward(heading_deg: float) -> Vec3:
    """Vetor de frente no mundo para um heading horário a partir do norte."""
    rad = math.radians(heading_deg)
    return (math.sin(rad), math.cos(rad), 0.0)


def rotate_to_heading(point: Vec3, heading_deg: float) -> Vec3:
    """Leva um ponto canônico para o mundo com o root girado em ``heading_deg``."""
    rad = -math.radians(heading_deg)
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    x, y, z = point
    return (x * cos_r - y * sin_r, x * sin_r + y * cos_r, z)


def vector_to_direction(east: float, north: float) -> str:
    """Quantiza um vetor de chão na direção canônica mais próxima."""
    if east == 0 and north == 0:
        raise ValueError("vetor nulo não tem direção")
    heading = math.degrees(math.atan2(east, north)) % 360.0
    return DIRECTION_ORDER[int((heading + 22.5) // 45.0) % 8]


def canonical_to_gltf(point: Vec3) -> Vec3:
    """Interno (x, y, z) → glTF (-x, z, y) (doc 17 §2).

    glTF: +Y cima, +Z frente, -X direita. O mapeamento preserva o sentido da base.
    """
    x, y, z = point
    return (-x, z, y)


@dataclass(frozen=True)
class CameraBasis:
    right: Vec3
    up: Vec3
    forward: Vec3
    location: Vec3
    ortho_scale: float

    def matrix_world(self) -> list[list[float]]:
        """Matriz 4×4 de câmera Blender (colunas right, up, -forward, location)."""
        r, u, f, c = self.right, self.up, self.forward, self.location
        return [
            [r[0], u[0], -f[0], c[0]],
            [r[1], u[1], -f[1], c[1]],
            [r[2], u[2], -f[2], c[2]],
            [0.0, 0.0, 0.0, 1.0],
        ]


def _dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def camera_basis(profile: RenderProfile, distance_m: float = 20.0) -> CameraBasis:
    """Câmera ortográfica fixa que projeta a origem do mundo exatamente no pivot."""
    elevation = math.radians(profile.elevation_deg)
    azimuth = math.radians(profile.azimuth_deg)
    sin_e, cos_e = math.sin(elevation), math.cos(elevation)
    sin_a, cos_a = math.sin(azimuth), math.cos(azimuth)
    forward = (sin_a * cos_e, cos_a * cos_e, -sin_e)
    right = (cos_a, -sin_a, 0.0)
    up = (sin_a * sin_e, cos_a * sin_e, cos_e)
    ppm = profile.pixels_per_meter
    offset_right = (profile.canvas.width / 2 - profile.pivot.x) / ppm
    offset_up = (profile.pivot.y - profile.canvas.height / 2) / ppm
    location = tuple(
        -f * distance_m + r * offset_right + u * offset_up
        for f, r, u in zip(forward, right, up, strict=True)
    )
    ortho_scale = max(profile.canvas.width, profile.canvas.height) / ppm
    return CameraBasis(right, up, forward, location, ortho_scale)  # type: ignore[arg-type]


def project_world(point: Vec3, profile: RenderProfile) -> tuple[float, float]:
    """Mundo → pixel contínuo do canvas (origem no canto superior esquerdo)."""
    basis = camera_basis(profile)
    ppm = profile.pixels_per_meter
    return (
        profile.pivot.x + ppm * _dot(point, basis.right),
        profile.pivot.y - ppm * _dot(point, basis.up),
    )


def project_canonical(point: Vec3, heading_deg: float, profile: RenderProfile) -> tuple[float, float]:
    return project_world(rotate_to_heading(point, heading_deg), profile)
