"""Julga os fatos coletados no Blender: RIG-001…004 e gate G4 (doc 17)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.domain.directions import project_canonical
from app.schemas.contracts import CheckResult, GateStatus, RenderProfile, RigProfile, Side

from engines.postprocess_engine.images import color_centroid, load_rgba

MOVED_MIN_M = 0.01
STATIC_MAX_M = 1e-4
MESH_SIDE_BAND_M = 0.02
PROJECTION_TOLERANCE_PX = 1.5
BIND_TOLERANCE_M = 0.001

MARKER_COLORS = {
    "hand_l": (0, 255, 0),
    "hand_r": (0, 0, 255),
    "foot_l": (255, 0, 255),
    "foot_r": (255, 255, 0),
    "qa_front": (0, 255, 255),
}


def _check(test_id: str, problems: list[str], ok: str, evidence: list[str] | None = None) -> CheckResult:
    return CheckResult(
        id=test_id,
        status=GateStatus.FAIL if problems else GateStatus.PASS,
        detail="; ".join(problems[:12]) if problems else ok,
        evidence=evidence or [],
    )


def check_hierarchy(rig: RigProfile, facts: dict[str, Any]) -> CheckResult:
    """RIG-001: existência, pais, conexões, deform, pares e lado em repouso."""
    problems: list[str] = []
    actual = {b["name"]: b for b in facts["bones"]}
    for spec in rig.bones:
        bone = actual.get(spec.blender_name)
        if bone is None:
            problems.append(f"ausente: {spec.blender_name}")
            continue
        if bone["parent"] != spec.parent:
            problems.append(f"{spec.blender_name}: pai {bone['parent']}, esperado {spec.parent}")
        if bone["connected"] != spec.connected:
            problems.append(f"{spec.blender_name}: conexão divergente")
        if bone["deform"] != spec.deform:
            problems.append(f"{spec.blender_name}: deform divergente")
        tolerance = rig.side_center_tolerance_m
        x = bone["head"][0]
        if spec.side is Side.LEFT and x > -tolerance:
            problems.append(f"{spec.blender_name}: lado LEFT com X={x:.3f}")
        if spec.side is Side.RIGHT and x < tolerance:
            problems.append(f"{spec.blender_name}: lado RIGHT com X={x:.3f}")
    extra = set(actual) - {b.blender_name for b in rig.bones}
    if extra:
        problems.append(f"ossos não documentados: {sorted(extra)}")
    by_role: dict[tuple[str, Side], int] = {}
    for spec in rig.bones:
        by_role[(spec.role, spec.side)] = by_role.get((spec.role, spec.side), 0) + 1
    for (role, side), count in by_role.items():
        if side is Side.LEFT and by_role.get((role, Side.RIGHT)) != count:
            problems.append(f"papel {role} sem par direito")
    for name, types in facts["ik"].items():
        if "IK" not in types:
            problems.append(f"cadeia {name} sem constraint IK")
    return _check("RIG-001", problems, f"{len(rig.bones)} ossos conferidos")


def check_sentinels(rig: RigProfile, facts: dict[str, Any]) -> CheckResult:
    """RIG-002: cada controle move só o membro esperado, no osso e na malha."""
    problems: list[str] = []
    results = {s["id"]: s for s in facts["sentinels"]}
    for sentinel in rig.sentinel_poses:
        result = results.get(sentinel.id)
        if result is None:
            problems.append(f"{sentinel.id}: não executado")
            continue
        for name in sentinel.expected_moved:
            if result["moved_m"][name] < MOVED_MIN_M:
                problems.append(f"{sentinel.id}: {name} não se moveu")
        for name in sentinel.expected_static:
            if result["moved_m"][name] > STATIC_MAX_M:
                problems.append(f"{sentinel.id}: {name} moveu {result['moved_m'][name]:.4f} m")
        if not result["mesh_finite"]:
            problems.append(f"{sentinel.id}: malha com NaN/Inf")
        if result["mesh_moved_vertices"] == 0:
            problems.append(f"{sentinel.id}: malha não deformou")
        elif sentinel.id.endswith("_left") and result["mesh_moved_x_range"][1] > MESH_SIDE_BAND_M:
            problems.append(f"{sentinel.id}: moveu malha do lado direito")
        elif sentinel.id.endswith("_right") and result["mesh_moved_x_range"][0] < -MESH_SIDE_BAND_M:
            problems.append(f"{sentinel.id}: moveu malha do lado esquerdo")
    return _check("RIG-002", problems, f"{len(rig.sentinel_poses)} poses movem o membro esperado")


def check_projection(
    rig: RigProfile, render: RenderProfile, facts: dict[str, Any]
) -> tuple[CheckResult, dict[str, dict[str, tuple[float, float]]]]:
    """RIG-003: pixel detectado × previsão independente pela matemática do perfil."""
    problems: list[str] = []
    detected: dict[str, dict[str, tuple[float, float]]] = {}
    heads = {b.blender_name: b.head for b in rig.bones}
    worst = 0.0
    for direction, path in facts["marker_renders"].items():
        rgba = load_rgba(Path(path))
        heading = render.headings_deg[direction]
        detected[direction] = {}
        for name, color in MARKER_COLORS.items():
            found = color_centroid(rgba, color, tolerance=40)
            if found is None:
                problems.append(f"{direction}: marcador {name} não encontrado")
                continue
            x, y, _ = found
            px, py = project_canonical(heads[name], heading, render)
            error = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
            worst = max(worst, error)
            detected[direction][name] = (x, y)
            if error > PROJECTION_TOLERANCE_PX:
                problems.append(f"{direction}/{name}: erro {error:.2f}px")
    check = CheckResult(
        id="RIG-003",
        status=GateStatus.FAIL if problems else GateStatus.PASS,
        detail="; ".join(problems[:12]) or f"5 marcadores em 8 direções; pior erro {worst:.2f}px",
        tolerance=f"{PROJECTION_TOLERANCE_PX}px",
        evidence=list(facts["marker_renders"].values()),
    )
    return check, detected


def check_skinning(rig: RigProfile, facts: dict[str, Any]) -> CheckResult:
    """RIG-004: pesos. Deformação visual segue para revisão humana."""
    problems: list[str] = []
    for item in facts["skin"]:
        name = item["object"]
        if item["no_influence"]:
            problems.append(f"{name}: {item['no_influence']} vértices sem peso")
        if item["bad_sum"]:
            problems.append(f"{name}: {item['bad_sum']} somas fora da tolerância")
        if item["max_influences"] > rig.max_influences:
            problems.append(f"{name}: {item['max_influences']} influências")
        if item["unknown_groups"]:
            problems.append(f"{name}: grupos sem osso {item['unknown_groups']}")
        if item["non_deform_groups"]:
            problems.append(f"{name}: grupos em osso não deformador {item['non_deform_groups']}")
        if item["crossed_side"]:
            problems.append(f"{name}: {item['crossed_side']} pesos do lado oposto")
    bind_error = facts["bind_error_m"]
    if bind_error > BIND_TOLERANCE_M:
        problems.append(f"pose de repouso desvia {bind_error * 1000:.2f} mm da malha de bind")
    return _check(
        "RIG-004", problems,
        f"{len(facts['skin'])} malhas com pesos válidos; bind {bind_error * 1000:.2f} mm",
    )


def validate_rig(rig: RigProfile, render: RenderProfile, facts: dict[str, Any]) -> list[CheckResult]:
    projection, _ = check_projection(rig, render, facts)
    return [
        check_hierarchy(rig, facts),
        check_sentinels(rig, facts),
        projection,
        check_skinning(rig, facts),
        CheckResult(
            id="RIG-REVIEW", status=GateStatus.REVIEW,
            detail="folha de poses sentinela aguarda revisão humana (doc 20 §5)",
            evidence=list(facts["sentinel_renders"].values())[:2],
        ),
    ]
