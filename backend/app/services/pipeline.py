"""Orquestra o pipeline com gates, cache por conteúdo e retomada (doc 07, doc 20).

Cada etapa vive em ``<personagem>/stages/<etapa>/<hash>``; o hash combina entradas, código e o
hash da etapa anterior. Alterar a câmera reaproveita montagem e animação; alterar uma cor
remonta. A etapa só conta como pronta depois do arquivo ``stage.done.json``: falha ou
cancelamento nunca deixa uma etapa parcial passar por completa, e nada apagado de etapas
anteriores nem da exportação publicada.
"""

from __future__ import annotations

import hashlib
import platform
import shutil
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import (
    BLENDER_SCRIPTS,
    REPO_ROOT,
    find_blender,
    read_json,
    sha256_file,
    sha256_json,
    tool_version,
    write_json,
)
from app.schemas.contracts import (
    BuildManifest,
    CheckResult,
    DirectionAtlas,
    ExportManifest,
    GateReport,
    GateStatus,
    ReleaseStatus,
    Stage,
)
from app.workers.blender_worker import run_stage
from engines.animation_engine.validate import validate_clip
from engines.character_engine.resolver import Library, Resolved, gate_g1_checks
from engines.export_engine import godot_bridge, package
from engines.postprocess_engine import atlas as atlas_engine
from engines.rig_engine.validate import validate_rig

Progress = Callable[[Stage, float | None, str], None]
RIGHT_ARM_FACTOR_WITH_WEAPON = 0.45
REQUIRED_HUMAN_GATES = ("G2", "G9")


def code_digest(*roots: Path) -> str:
    digest = hashlib.sha256()
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            digest.update(path.relative_to(REPO_ROOT).as_posix().encode())
            digest.update(sha256_file(path).encode())
    return digest.hexdigest()


class PipelineFailure(RuntimeError):
    def __init__(self, stage: Stage, message: str, reports: list[GateReport]):
        super().__init__(f"{stage.value}: {message}")
        self.stage = stage
        self.reports = reports


class SimulatedFailure(RuntimeError):
    """Injetada por teste de recuperação (CA-011)."""


@dataclass
class RunResult:
    character_dir: Path
    reports: list[GateReport]
    export_dir: Path | None
    release: ReleaseStatus | None
    metrics: dict[str, Any] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)
    cache_hits: list[str] = field(default_factory=list)


class Pipeline:
    def __init__(
        self,
        project_dir: Path,
        *,
        progress: Progress | None = None,
        cancel: threading.Event | None = None,
        fail_at: Stage | None = None,
        library: Library | None = None,
    ):
        self.project_dir = project_dir
        self.progress = progress or (lambda stage, value, message: None)
        self.cancel = cancel
        self.fail_at = fail_at
        self.library = library or Library()
        self.reports: list[GateReport] = []
        self.timings: dict[str, float] = {}
        self.cache_hits: list[str] = []
        self.versions: dict[str, str] = {}

    # --- infraestrutura ------------------------------------------------------
    def _gate(self, gate: str, checks: list[CheckResult]) -> GateReport:
        report = GateReport.from_checks(gate, checks)
        self.reports.append(report)
        write_json(self.character_dir / "gates" / f"{gate}.json", report.model_dump(mode="json"))
        return report

    def _require(self, stage: Stage, report: GateReport) -> None:
        if report.status in (GateStatus.FAIL, GateStatus.REJECTED, GateStatus.NOT_TESTED):
            failed = [c for c in report.checks if c.status not in (GateStatus.PASS, GateStatus.REVIEW, GateStatus.WARN)]
            detail = "; ".join(f"{c.id}: {c.detail}" for c in failed[:4])
            raise PipelineFailure(stage, f"gate {report.gate} bloqueou: {detail}", self.reports)

    def _maybe_fail(self, stage: Stage) -> None:
        if self.fail_at is stage:
            raise SimulatedFailure(f"falha simulada em {stage.value}")

    def _stage(self, name: str, digest: str, work: Callable[[Path], dict[str, Any]]) -> tuple[Path, dict[str, Any]]:
        folder = self.character_dir / "stages" / name / digest[:16]
        done = folder / "stage.done.json"
        if done.is_file():
            self.cache_hits.append(name)
            return folder, read_json(done)
        if folder.exists():
            shutil.rmtree(folder)  # resíduo de tentativa interrompida, nunca marcado como pronto
        folder.mkdir(parents=True)
        started = time.monotonic()
        output = work(folder)
        self.timings[name] = round(time.monotonic() - started, 2)
        write_json(done, output)
        return folder, output

    def _record_environment(self) -> None:
        blender = find_blender()
        self.versions = {
            "os": platform.platform(),
            "python": platform.python_version(),
            "blender": tool_version(blender, "--version"),
        }

    # --- pipeline -----------------------------------------------------------
    def run(
        self,
        spec_data: dict[str, Any],
        *,
        run_godot: bool = True,
        godot_window: bool = True,
        publish_to: Path | None = None,
    ) -> RunResult:
        slug = spec_data.get("slug", "invalid")
        self.character_dir = self.project_dir / "characters" / str(slug)
        self.character_dir.mkdir(parents=True, exist_ok=True)
        self.progress(Stage.SPEC_VALIDATION, 0.02, "Validando especificação")
        resolved, checks = gate_g1_checks(spec_data, self.library)
        report = self._gate("G1", checks)
        self._require(Stage.SPEC_VALIDATION, report)
        assert resolved is not None
        self.resolved = resolved
        self._maybe_fail(Stage.SPEC_VALIDATION)
        self._record_environment()
        write_json(self.character_dir / "character_spec.json", resolved.spec.model_dump(mode="json"))
        scripts = code_digest(BLENDER_SCRIPTS)

        blend_dir, build = self._build(resolved, scripts)
        rig_dir, rig_facts = self._rig(resolved, blend_dir, scripts)
        anim_dir, traces = self._animate(resolved, blend_dir, scripts)
        render_dir, frames = self._render(resolved, anim_dir, scripts)
        atlases, qa_checks, metrics = self._post(resolved, render_dir, frames, traces)
        return self._export(
            resolved, blend_dir, anim_dir, build, rig_dir, rig_facts, render_dir, atlases,
            qa_checks, metrics, run_godot, godot_window, publish_to, scripts,
        )

    def _build(self, r: Resolved, scripts: str) -> tuple[Path, dict[str, Any]]:
        self.progress(Stage.BUILD, 0.08, "Montando personagem no Blender")
        payload = r.build_payload(Path("placeholder"))
        payload.pop("blend_path")
        digest = sha256_json({"payload": payload, "code": scripts})

        def work(folder: Path) -> dict[str, Any]:
            blend = folder / "character.blend"
            run = run_stage("build", r.build_payload(blend), folder, timeout_s=300, cancel=self.cancel)
            manifest = BuildManifest(
                character_id=r.spec.id, spec_sha256=sha256_json(r.spec.model_dump(mode="json")),
                builder_version=run.output["builder_version"],
                blender_version=run.output["blender_version"], source_scene="character.blend",
                source_scene_sha256=sha256_file(blend), components=r.uses,
                materials=run.output["materials"], objects=run.output["objects"],
            )
            write_json(folder / "build_manifest.json", manifest.model_dump(mode="json"))
            return run.output

        folder, output = self._stage("build", digest, work)
        report = self._gate("G3", self._build_checks(r, output))
        self._require(Stage.BUILD, report)
        self._maybe_fail(Stage.BUILD)
        return folder, output

    @staticmethod
    def _build_checks(r: Resolved, output: dict[str, Any]) -> list[CheckResult]:
        components = {o["component"] for o in output["objects"]}
        wanted = {c.id for c in r.components}
        missing = sorted(wanted - components)
        empty = [o["name"] for o in output["objects"] if o["vertices"] == 0]
        return [
            CheckResult(
                id="BLD-001",
                status=GateStatus.FAIL if missing or empty else GateStatus.PASS,
                detail=f"faltam {missing} / vazios {empty}" if missing or empty else
                f"{len(components)} componentes em {len(output['objects'])} malhas",
            ),
            CheckResult(id="ART-002", status=GateStatus.REVIEW,
                        detail="silhueta e modelo aguardam revisão humana"),
        ]

    def _rig(self, r: Resolved, blend_dir: Path, scripts: str) -> tuple[Path, dict[str, Any]]:
        self.progress(Stage.RIG, 0.2, "Validando rig e poses sentinela")
        digest = sha256_json({
            "build": blend_dir.name, "render": r.render_payload(), "rig": r.rig.model_dump(mode="json"),
            "code": scripts,
        })

        def work(folder: Path) -> dict[str, Any]:
            payload = {
                "render": r.render_payload(), "rig": r.rig.model_dump(mode="json"),
                "headings": r.render.headings_deg, "output_dir": str(folder),
            }
            return run_stage("rig_check", payload, folder, blend_file=blend_dir / "character.blend",
                             timeout_s=300, cancel=self.cancel).output

        folder, facts = self._stage("rig", digest, work)
        report = self._gate("G4", validate_rig(r.rig, r.render, facts))
        self._require(Stage.RIG, report)
        self._maybe_fail(Stage.RIG)
        return folder, facts

    def _animate(self, r: Resolved, blend_dir: Path, scripts: str) -> tuple[Path, dict[str, Any]]:
        self.progress(Stage.ANIMATION, 0.3, "Aplicando animações")
        clips = [c.model_dump(mode="json") for c in r.animation.clips]
        factor = RIGHT_ARM_FACTOR_WITH_WEAPON if r.spec.outfit.weapon_asset else 1.0
        digest = sha256_json({"build": blend_dir.name, "clips": clips, "factor": factor, "code": scripts})

        def work(folder: Path) -> dict[str, Any]:
            blend = folder / "character.blend"
            shutil.copy2(blend_dir / "character.blend", blend)
            bones = {b.blender_name: b for b in r.rig.bones}
            foot = (bones["heel_l"].head[1], bones["ball_l"].head[1], bones["foot_l"].head[2])
            hands = [a for c in r.components if c.kind == "weapon" for a in c.anchors]
            weapon_side = "l" if "hand_l" in hands else "r"
            payload = {"clips": clips, "right_arm_factor": factor, "foot": foot,
                       "weapon_side": weapon_side, "blend_path": str(blend)}
            return run_stage("animate", payload, folder, blend_file=blend, timeout_s=300,
                             cancel=self.cancel).output

        folder, output = self._stage("animate", digest, work)
        traces = output["traces"]
        checks: list[CheckResult] = []
        metrics = []
        for clip in r.animation.clips:
            clip_checks, clip_metrics = validate_clip(clip, r.rig, traces[clip.animation_id])
            checks += clip_checks
            metrics.append(clip_metrics)
        write_json(folder / "animation_validation.json", metrics)
        report = self._gate("G5", checks)
        self._require(Stage.ANIMATION, report)
        self._maybe_fail(Stage.ANIMATION)
        return folder, traces

    def _render(self, r: Resolved, anim_dir: Path, scripts: str) -> tuple[Path, dict[str, Any]]:
        self.progress(Stage.RENDER, 0.4, "Renderizando oito direções")
        clips = [c.model_dump(mode="json") for c in r.animation.clips]
        pixel = r.art.pixel.model_dump(mode="json") if r.art.pixel else None
        smooth = r.art.smooth.model_dump(mode="json") if r.art.smooth else None
        composed = pixel or smooth
        digest = sha256_json({"anim": anim_dir.name, "render": r.render_payload(), "code": scripts, "pixel": pixel,
                              "smooth": smooth,
                              "compose": code_digest(REPO_ROOT / "engines" / "postprocess_engine") if composed else None})

        def work(folder: Path) -> dict[str, Any]:
            frames = folder / "frames"
            frames.mkdir()
            if composed:
                return self._render_composed(r, anim_dir, folder, frames, clips, "smooth" if smooth else "pixel")
            payload = {"clips": clips, "render": r.render_payload(), "output_dir": str(frames),
                       "progress_file": str(folder / "progress.json")}
            total = sum(c["frame_count"] for c in clips) * 8
            stop = threading.Event()

            def watch() -> None:
                while not stop.wait(1.0):
                    try:
                        data = read_json(folder / "progress.json")
                    except (OSError, ValueError):
                        continue
                    self.progress(Stage.RENDER, 0.4 + 0.45 * data["done"] / total,
                                  f"Renderizando {data['done']}/{total}")

            watcher = threading.Thread(target=watch, daemon=True)
            watcher.start()
            try:
                return run_stage("render", payload, folder, blend_file=anim_dir / "character.blend",
                                 timeout_s=1800, cancel=self.cancel).output
            finally:
                stop.set()
                watcher.join()

        folder, output = self._stage("render", digest, work)
        self._maybe_fail(Stage.RENDER)
        return folder, output["frames"]

    def _render_composed(self, r: Resolved, anim_dir: Path, folder: Path, frames: Path,
                         clips: list[dict[str, Any]], mode: str) -> dict[str, Any]:
        """Acabamentos por passes nativos (id, luz, profundidade) + composição em Python.

        ``pixel``: grade final, alpha binário (engines/postprocess_engine/pixel.py).
        ``smooth``: passes em N× e redução com antialiasing (engines/postprocess_engine/smooth.py).
        """
        if mode == "smooth":
            from engines.postprocess_engine.smooth import compose_folder
            cfg = r.art.smooth
            scale = cfg.supersample
        else:
            from engines.postprocess_engine.pixel import compose_folder
            cfg = r.art.pixel
            scale = 1
        render = r.render_payload()
        render["canvas"] = {"width": render["canvas"]["width"] * scale, "height": render["canvas"]["height"] * scale}
        passes = folder / "passes"
        passes.mkdir()
        payload = {"clips": clips, "render": render, "output_dir": str(passes), "pixel": cfg.model_dump(mode="json")}
        self.progress(Stage.RENDER, 0.45, f"Renderizando passes ({mode})")
        output = run_stage("pixel_passes", payload, folder, blend_file=anim_dir / "character.blend",
                           timeout_s=5400, cancel=self.cancel).output
        self.progress(Stage.RENDER, 0.75, f"Compondo ({mode})")
        index = compose_folder(passes, frames, cfg, clips, r.render.direction_order,
                               tuple(output["depth_range_m"]))
        return {"frames": index, "passes": output}

    def _post(self, r: Resolved, render_dir: Path, frames: dict[str, Any], traces: dict[str, Any]):
        self.progress(Stage.POST_PROCESS, 0.87, "Montando atlases e conferindo imagens")
        digest = sha256_json({"render": render_dir.name, "code": code_digest(REPO_ROOT / "engines" / "postprocess_engine")})

        def work(folder: Path) -> dict[str, Any]:
            atlas_dir = folder / "atlases"
            qa_dir = folder / "qa"
            qa_dir.mkdir()
            atlases: dict[str, dict[str, Any]] = {}
            checks: list[CheckResult] = []
            metrics: dict[str, Any] = {}
            atlas_problems: list[str] = []
            sequence_problems: list[str] = []
            for clip in r.animation.clips:
                cid = clip.animation_id
                clip_frames = {d: [Path(p) for p in files] for d, files in frames[cid].items()}
                entry = {}
                for direction, files in clip_frames.items():
                    out = atlas_dir / f"{cid}_{direction}.png"
                    atlas = atlas_engine.build_atlas(files, out, r.render, r.render.headings_deg[direction])
                    atlas_problems += atlas_engine.check_atlas(out, atlas, files)
                    entry[direction] = atlas.model_dump(mode="json")
                atlases[cid] = entry
                clip_checks, clip_metrics = atlas_engine.qa_frames(clip, r.render, clip_frames, traces[cid])
                checks += clip_checks
                metrics[cid] = clip_metrics
                atlas_engine.contact_sheet(
                    {d: f[0] for d, f in clip_frames.items()}, qa_dir / f"contact_{cid}.png",
                    f"{r.spec.name}\n{cid} / frame 0\nfps {clip.fps}\nN = norte do mapa\nstatus: UNAPPROVED",
                    r.render,
                )
                atlas_engine.spritesheet_preview(
                    {d: atlas_dir / f"{cid}_{d}.png" for d in r.render.direction_order},
                    qa_dir / f"sheet_{cid}.png",
                )
                for direction in ("S", "E"):
                    atlas_engine.animated_preview(
                        clip_frames[direction], qa_dir / f"preview_{cid}_{direction}.gif", clip.fps
                    )
            checks.append(CheckResult(
                id="IMG-003", status=GateStatus.FAIL if atlas_problems else GateStatus.PASS,
                detail="; ".join(atlas_problems[:6]) or "atlases íntegros e idênticos aos frames",
            ))
            del sequence_problems
            return {
                "atlases": atlases, "metrics": metrics,
                "checks": [c.model_dump(mode="json") for c in checks],
            }

        folder, output = self._stage("post", digest, work)
        checks = [CheckResult.model_validate(c) for c in output["checks"]]
        report = self._gate("G6", checks)
        self._require(Stage.VALIDATION, report)
        self._maybe_fail(Stage.POST_PROCESS)
        atlases = {
            clip: {d: DirectionAtlas.model_validate(a) for d, a in entry.items()}
            for clip, entry in output["atlases"].items()
        }
        return (folder, atlases), checks, output["metrics"]

    def approvals(self) -> dict[str, Any]:
        path = self.character_dir / "approvals.json"
        return read_json(path) if path.is_file() else {}

    def _human_status(self) -> tuple[bool, list[CheckResult]]:
        approvals = self.approvals()
        checks = []
        spec_hash = sha256_json(self.resolved.spec.model_dump(mode="json"))
        for gate, name in (("G2", "conceito"), ("G9", "arte final")):
            record = approvals.get(gate)
            if record and record.get("spec_sha256") == spec_hash:
                status = GateStatus(record["status"])
                detail = f"{record['status']} por {record['reviewer']} em {record['at']}"
            else:
                status, detail = GateStatus.REVIEW, f"aprovação humana de {name} pendente"
            checks.append(CheckResult(id=f"HUMAN-{gate}", status=status, detail=detail))
        return all(c.status is GateStatus.APPROVED for c in checks), checks

    def _export(self, r, blend_dir, anim_dir, build, rig_dir, rig_facts, render_dir, post, qa_checks,
                metrics, run_godot, godot_window, publish_to, scripts) -> RunResult:
        self.progress(Stage.EXPORT, 0.92, "Gerando pacote")
        post_dir, atlases = post
        glb = self._glb(anim_dir, scripts)
        job_tag = time.strftime("%Y%m%dT%H%M%S")
        staging = self.character_dir / "exports_staging" / job_tag
        extras = {f"qa/{p.name}": p for p in sorted((post_dir / "qa").glob("*"))}
        extras["source/character.glb"] = glb
        extras["source/build_manifest.json"] = blend_dir / "build_manifest.json"
        for gate_file in sorted((self.character_dir / "gates").glob("G[0-9].json")):
            extras[f"qa/gates/{gate_file.name}"] = gate_file
        all_auto = [c for report in self.reports for c in report.checks]
        approved, human_checks = self._human_status()
        all_checks = all_auto + human_checks
        godot_pending = CheckResult(id="GODOT-001", status=GateStatus.NOT_TESTED, detail="pendente")
        release = package.release_for([*all_checks, godot_pending], approved)
        package.stage_export(
            staging, r.spec, r.render, r.animation, atlases, post_dir / "atlases",
            anim_dir / "character.blend", extras, build["blender_version"], release, approved,
        )
        problems = package.verify_manifest(staging)
        self._gate("G7", [
            CheckResult(id="EXP-001", status=GateStatus.FAIL if problems else GateStatus.PASS,
                        detail="; ".join(problems[:6]) or "manifesto corresponde aos arquivos"),
            CheckResult(id="EXP-002", status=GateStatus.FAIL if problems else GateStatus.PASS,
                        detail="hashes, tamanhos e metadados coerentes" if not problems else "ver EXP-001"),
        ])
        self._require(Stage.EXPORT, self.reports[-1])
        self._maybe_fail(Stage.EXPORT)

        if run_godot:
            self.progress(Stage.RUNTIME, 0.95, "Testando no Godot")
            manifest = ExportManifest.model_validate(read_json(staging / "manifest.json"))
            godot = godot_bridge.run_godot_checks(
                staging, manifest, r.spec.slug, self.character_dir / "godot", windowed=godot_window
            )
            metrics["godot"] = godot.report
            self._gate("G8", godot.checks)
            self._require(Stage.RUNTIME, self.reports[-1])
            final = package.release_for(
                [c for report in self.reports for c in report.checks] + human_checks, approved
            )
            package.stamp_runtime(staging, godot.version, final)
            release = final
            shutil.copy2(self.character_dir / "gates" / "G8.json", staging / "qa" / "gates" / "G8.json")
            self._refresh_manifest(staging)
        else:
            self._gate("G8", [CheckResult(id="GODOT-001", status=GateStatus.NOT_TESTED, detail="não solicitado")])

        self._gate("G9", human_checks)
        export_dir = None
        if publish_to is not None:
            export_dir = package.publish(staging, publish_to)
        self.progress(Stage.EXPORT, 1.0, f"Concluído: {release.value}")
        return RunResult(
            self.character_dir, self.reports, export_dir, release, metrics, self.timings, self.cache_hits
        )

    @staticmethod
    def _refresh_manifest(staging: Path) -> None:
        data = read_json(staging / "manifest.json")
        data["files"] = [e.model_dump(mode="json") for e in package._file_entries(staging)]
        write_json(staging / "manifest.json", ExportManifest.model_validate(data).model_dump(mode="json"))

    def _glb(self, anim_dir: Path, scripts: str) -> Path:
        digest = sha256_json({"anim": anim_dir.name, "code": scripts})

        def work(folder: Path) -> dict[str, Any]:
            return run_stage("export_glb", {"glb_path": str(folder / "character.glb")}, folder,
                             blend_file=anim_dir / "character.blend", timeout_s=300,
                             cancel=self.cancel).output

        folder, _ = self._stage("glb", digest, work)
        return folder / "character.glb"
