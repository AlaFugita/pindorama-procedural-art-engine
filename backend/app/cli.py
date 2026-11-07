"""CLI ``ics``: toda operação central fica acessível sem interface (RNF-011)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.core.config import PROJECTS_DIR, REPO_ROOT, read_json, write_json
from app.schemas.contracts import ALL_CONTRACTS, Stage


def cmd_schemas(args: argparse.Namespace) -> int:
    out = REPO_ROOT / "schemas"
    for name, model in ALL_CONTRACTS.items():
        write_json(out / f"{name}.schema.json", model.model_json_schema())
    print(f"{len(ALL_CONTRACTS)} schemas em {out}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    from app.services.environment import collect

    report = collect()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


def cmd_run(args: argparse.Namespace) -> int:
    from app.services.pipeline import Pipeline, PipelineFailure

    sys.stdout.reconfigure(encoding="utf-8")
    spec = read_json(Path(args.spec))

    def show(stage: Stage, progress: float | None, message: str) -> None:
        print(f"[{stage.value}] {progress or 0:5.0%} {message}", flush=True)

    project = Path(args.project) if args.project else PROJECTS_DIR / "default"
    pipeline = Pipeline(project, progress=show)
    publish = Path(args.export) / spec["slug"] if args.export else REPO_ROOT / "exports" / spec["slug"]
    try:
        result = pipeline.run(spec, run_godot=not args.no_godot, godot_window=not args.headless,
                              publish_to=publish)
    except PipelineFailure as failure:
        print(f"FALHOU: {failure}", file=sys.stderr)
        for report in failure.reports:
            print(f"  {report.gate}: {report.status.value}")
        return 2
    for report in result.reports:
        print(f"{report.gate}: {report.status.value}")
        for check in report.checks:
            print(f"   {check.status.value:10} {check.id}: {check.detail}")
    print(f"release: {result.release.value}\npacote: {result.export_dir}")
    print(f"tempos: {result.timings}\ncache: {result.cache_hits}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    from app.services.approvals import record

    path = record(Path(args.character_dir), args.gate, args.status, args.reviewer, args.comment or "")
    print(f"registrado em {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ics")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("schemas", help="gera JSON Schema dos contratos").set_defaults(func=cmd_schemas)
    sub.add_parser("doctor", help="inventário do ambiente").set_defaults(func=cmd_doctor)
    run = sub.add_parser("run", help="executa o pipeline para um CharacterSpec")
    run.add_argument("spec")
    run.add_argument("--project")
    run.add_argument("--export")
    run.add_argument("--no-godot", action="store_true")
    run.add_argument("--headless", action="store_true", help="não abre janela no teste Godot")
    run.set_defaults(func=cmd_run)
    approve = sub.add_parser("approve", help="registra decisão humana")
    approve.add_argument("character_dir")
    approve.add_argument("gate", choices=["G2", "G3M", "G9"])
    approve.add_argument("status", choices=["APPROVED", "REJECTED"])
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--comment")
    approve.set_defaults(func=cmd_approve)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
