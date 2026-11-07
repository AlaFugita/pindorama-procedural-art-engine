"""Registro de decisões humanas (doc 20 §6), vinculado ao hash do CharacterSpec.

O estado vigente fica por gate; todo registro anterior permanece em ``history``, de modo que
uma aprovação futura nunca apaga uma reprovação.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.core.config import read_json, sha256_json, write_json


def record(character_dir: Path, gate: str, status: str, reviewer: str, comment: str = "") -> Path:
    if not reviewer.strip():
        raise ValueError("revisor obrigatório")
    spec = read_json(character_dir / "character_spec.json")
    path = character_dir / "approvals.json"
    approvals = read_json(path) if path.is_file() else {}
    previous = approvals.get(gate)
    if previous is not None:
        approvals.setdefault("history", []).append({"gate": gate, **previous})
    approvals[gate] = {
        "status": status, "reviewer": reviewer, "comment": comment,
        "at": datetime.now(UTC).isoformat(), "spec_sha256": sha256_json(spec),
    }
    return write_json(path, approvals)
