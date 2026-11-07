"""Validação temporal por clip: ANI-001…004 e gate G5 (doc 18). Unidades normalizadas por H."""

from __future__ import annotations

import math
from typing import Any

from app.schemas.contracts import AnimationClip, CheckResult, GateStatus, RigProfile

KNEE_EPS_M2 = 1e-5
SEMANTIC_LANDMARKS = ("pelvis", "head", "hand_l", "hand_r", "foot_l", "foot_r")


def _dist(a: list[float], b: list[float]) -> float:
    return math.dist(a, b)


def stance_frames(clip: AnimationClip, side: str) -> set[int]:
    """Frames de apoio do pé, derivados só dos eventos declarados (com ciclo)."""
    prefix = "LEFT" if side == "l" else "RIGHT"
    contact = next((e.frame for e in clip.events if e.event == f"{prefix}_FOOT_CONTACT"), None)
    swing = next((e.frame for e in clip.events if e.event == f"{prefix}_SWING"), None)
    if contact is None:
        return set()
    n = clip.frame_count
    if swing is None:
        return set(range(n))
    frames, frame = set(), contact
    while True:
        frames.add(frame)
        if frame == swing:
            return frames
        frame = (frame + 1) % n


def validate_clip(
    clip: AnimationClip, rig: RigProfile, trace: list[dict[str, Any]]
) -> tuple[list[CheckResult], dict[str, Any]]:
    tol = clip.tolerances
    height = rig.reference_height_m
    n = clip.frame_count
    dt = 1.0 / clip.fps
    cid = clip.animation_id
    metrics: dict[str, Any] = {"animation_id": cid, "frames": len(trace)}
    points = [f["points"] for f in trace]

    integrity: list[str] = []
    if [f["frame"] for f in trace] != list(range(n + 1)):
        integrity.append("frames avaliados incompletos")
    if not all(f["finite"] for f in trace):
        integrity.append("pose com NaN/Inf")
    ik_error = max(
        _dist(p[f"foot_{s}"], p[f"ik_foot_{s}"]) for p in points for s in "lr"
    ) / height
    metrics["ik_error_h"] = ik_error
    if ik_error > tol.ik_error_h:
        integrity.append(f"pé não alcança o alvo IK: {ik_error:.4f}H")
    for index, p in enumerate(points):
        for side in "lr":
            hip, knee, ankle = p[f"thigh_{side}"], p[f"shin_{side}"], p[f"foot_{side}"]
            dy, dz = ankle[1] - hip[1], ankle[2] - hip[2]
            ky, kz = knee[1] - hip[1], knee[2] - hip[2]
            if dy * kz - dz * ky < -KNEE_EPS_M2:
                integrity.append(f"joelho {side} dobra para trás no frame {index}")
    if clip.gait.stride_m > 0:
        expected = clip.gait.stride_m / (clip.duration_s * clip.gait.stance_fraction)
        if abs(expected - clip.ground_speed_mps) > 0.01 * expected:
            integrity.append("ground_speed_mps incoerente com passada")

    contact: list[str] = []
    slide: list[str] = []
    worst_slide = 0.0
    lowest = min(p[k][2] for p in points for k in ("heel_l", "heel_r", "ball_l", "ball_r"))
    metrics["lowest_contact_point_h"] = lowest / height
    if -lowest / height > tol.ground_penetration_h:
        contact.append(f"penetração no chão {lowest / height:.4f}H")
    for side in "lr":
        stance = stance_frames(clip, side)
        if not stance:
            contact.append(f"pé {side} sem evento de contato")
            continue
        heights = [
            max(points[f][f"heel_{side}"][2], points[f][f"ball_{side}"][2]) for f in sorted(stance)
        ]
        peak = max(heights) / height
        metrics[f"stance_height_h_{side}"] = peak
        if peak > tol.contact_height_h:
            contact.append(f"pé {side} flutua no apoio: {peak:.4f}H")
        swing = set(range(n)) - stance
        if swing:
            lift = max(points[f][f"heel_{side}"][2] for f in swing) / height
            metrics[f"swing_lift_h_{side}"] = lift
            if lift <= tol.contact_height_h:
                contact.append(f"pé {side} não sai do chão no balanço")
        for frame in sorted(stance):
            following = frame + 1
            if following % n not in stance:
                continue
            for key in (f"heel_{side}", f"ball_{side}"):
                now, after = points[frame][key], points[following][key]
                vy = (after[1] - now[1]) / dt + clip.ground_speed_mps
                vx = (after[0] - now[0]) / dt
                speed = math.hypot(vx, vy) / height
                worst_slide = max(worst_slide, speed)
    metrics["foot_slide_h_per_s"] = worst_slide
    if worst_slide > tol.foot_slide_speed_h_per_s:
        slide.append(f"foot sliding {worst_slide:.4f} H/s")

    steps = [
        max(_dist(points[i][k], points[i + 1][k]) for k in SEMANTIC_LANDMARKS) / height
        for i in range(n - 1)
    ]
    loop_gap = max(_dist(points[n][k], points[0][k]) for k in SEMANTIC_LANDMARKS) / height
    closing = max(_dist(points[n - 1][k], points[n][k]) for k in SEMANTIC_LANDMARKS) / height
    root_gap = _dist(points[n]["root"], points[0]["root"]) / height
    metrics.update(max_step_h=max(steps), loop_gap_h=loop_gap, closing_step_h=closing)
    loop: list[str] = []
    if clip.loop:
        if loop_gap > 1e-3:
            loop.append(f"frame final difere do inicial: {loop_gap:.5f}H")
        if root_gap > 1e-5:
            loop.append("root desloca no ciclo in_place")
        if closing > max(max(steps) * tol.loop_landmark_gap_factor, 1e-3):
            loop.append(f"salto no fechamento: {closing:.4f}H × passo {max(steps):.4f}H")
    if max(steps) > tol.max_landmark_step_h:
        loop.append(f"salto entre frames: {max(steps):.4f}H")

    def result(suffix: str, problems: list[str], ok: str) -> CheckResult:
        return CheckResult(
            id=f"{suffix}:{cid}",
            status=GateStatus.FAIL if problems else GateStatus.PASS,
            detail="; ".join(problems) or ok,
        )

    return [
        result("ANI-001", integrity, f"{n} frames + fechamento avaliados; IK {ik_error:.5f}H"),
        result("ANI-002", contact, f"contatos coerentes; mínimo {lowest / height:.4f}H"),
        CheckResult(
            id=f"ANI-003:{cid}",
            status=GateStatus.FAIL if slide else GateStatus.PASS,
            detail="; ".join(slide) or f"foot sliding {worst_slide:.5f} H/s",
            tolerance=f"{tol.foot_slide_speed_h_per_s} H/s",
        ),
        result("ANI-004", loop, f"loop {loop_gap:.6f}H; maior passo {max(steps):.4f}H"),
        CheckResult(id=f"ANI-REVIEW:{cid}", status=GateStatus.REVIEW,
                    detail="qualidade do movimento exige revisão humana"),
    ], metrics
