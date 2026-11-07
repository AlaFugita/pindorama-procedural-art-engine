"""Gera os dados e os GIFs reais da página Animation Showcase & Validation.

Status por ação × direção, derivado SÓ de testes executados:
- FAIL: algum check do clip falhou (gates G5/G6, Godot GODOT-001/003);
- WARN: passou com ressalva (ex.: quadros repetidos acidentais, ANI-005 em aviso);
- PASS: gates do clip aprovados E o Godot importou, tocou na velocidade e na sequência certas
  E os cenários de estado desse clip passaram;
- NOT TESTED: existe, mas o Godot não rodou para o personagem;
- MISSING: ação do catálogo sem clip implementado.
Um GIF existir não muda o status.

Uso: python scripts/build_animation_showcase.py <slug> [<slug> ...]
"""

import json
import shutil
import sys
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "showcase"
DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
BG = (164, 186, 150)

# Catálogo pedido: (categoria, ação, clip que a implementa ou None, observação)
CATALOG = [
    ("Locomoção", "Idle", "idle", ""),
    ("Locomoção", "Walking", "walk", ""),
    ("Locomoção", "Running", "run", ""),
    ("Locomoção", "Falling", None, "Exige deslocamento vertical da raiz; o pipeline é in_place"),
    ("Locomoção", "Landing", None, "Depende de Falling"),
    ("Locomoção", "Jumping", None, "Exige raiz com altura (root motion vertical) e evento de decolagem"),
    ("Corpo a corpo", "Melee Attack", "attack_melee", "Golpe de cajado (arma equipada)"),
    ("Corpo a corpo", "Ataque com arma equipada", "attack_melee", "Mesmo clip: o cajado está na mão esquerda"),
    ("Corpo a corpo", "Ataques por tipo de arma", None, "Espada, maça, lança e duas mãos precisam de WeaponProfile"),
    ("Corpo a corpo", "Sequência de ataques", "attack_melee", "Combo de 2 pela fila do controlador; sem clip de combo próprio"),
    ("À distância", "Shooting", None, "Não há arco nem arma de disparo no personagem"),
    ("À distância", "Aiming", None, ""),
    ("À distância", "Throwing", None, ""),
    ("À distância", "Lançamento de projéteis", None, "Evento existe só em CAST_RELEASE; sem projétil"),
    ("À distância", "Recuperação após disparo", None, ""),
    ("Magia", "Magic Casting", "cast", "Fases prepare 0–5, execute 6–7, recover 8–11"),
    ("Magia", "Preparação da magia", "cast", "Fase prepare do clip cast"),
    ("Magia", "Execução do lançamento", "cast", "Fase execute; evento CAST_RELEASE no quadro 7"),
    ("Magia", "Recuperação após lançamento", "cast", "Fase recover; interrompível a partir do quadro 8"),
    ("Magia", "Habilidades especiais", None, ""),
    ("Interação", "Interacting", "interact", "Alcance com a mão livre; evento INTERACT"),
    ("Interação", "Coletar objetos", None, "Pode reutilizar interact; sem clip próprio (abaixar até o chão)"),
    ("Interação", "Utilizar objetos", None, ""),
    ("Interação", "Abrir/manipular cenário", None, ""),
    ("Interação", "Interagir com NPCs", None, "Pode reutilizar interact ou idle; sem clip próprio"),
    ("Interação", "Utilizar equipamentos", None, ""),
    ("Estados", "Taking Damage", "hurt", ""),
    ("Estados", "Stunned", None, ""),
    ("Estados", "Death", "death", "Terminal; último quadro mantido de propósito"),
    ("Estados", "Respawn", None, ""),
]


def gate_checks(slug):
    checks = []
    for gate in ("G5", "G6", "G8"):
        path = ROOT / "exports" / slug / "qa" / "gates" / f"{gate}.json"
        if path.exists():
            checks += json.loads(path.read_text(encoding="utf-8"))["checks"]
    return checks


def latest(path):
    return max(path.iterdir(), key=lambda p: p.stat().st_mtime)


def build(slug):
    manifest = json.loads((ROOT / "exports" / slug / "manifest.json").read_text(encoding="utf-8"))
    checks = gate_checks(slug)
    godot_dir = ROOT / "projects/default/characters" / slug / "godot"
    smoke = json.loads((godot_dir / "godot_smoke.json").read_text(encoding="utf-8")) if (godot_dir / "godot_smoke.json").exists() else None
    states = json.loads((godot_dir / "godot_states.json").read_text(encoding="utf-8")) if (godot_dir / "godot_states.json").exists() else None
    render = latest(ROOT / "projects/default/characters" / slug / "stages/render")
    out = OUT / slug
    (out / "atlas").mkdir(parents=True, exist_ok=True)
    clips = {}
    for anim in manifest["animations"]:
        cid = anim["animation"]
        own = [c for c in checks if c["id"].endswith(f":{cid}")]
        statuses = {c["status"] for c in own}
        scenario = next((s for s in (states or {}).get("scenarios", []) if s["name"] == f"clip:{cid}"), None)
        transitions = [s for s in (states or {}).get("scenarios", []) if cid in s["actions"] and not s["name"].startswith("clip:")]
        per_dir = {}
        for d in DIRS:
            smoke_fail = [f for f in (smoke or {}).get("failures", []) if f.startswith(f"{cid}_{d}")]
            if smoke is None or states is None:
                status = "NOT TESTED"
            elif "FAIL" in statuses or smoke_fail or (scenario and scenario["status"] == "FAIL") or any(t["status"] == "FAIL" for t in transitions):
                status = "FAIL"
            elif "WARN" in statuses:
                status = "WARN"
            else:
                status = "PASS"
            frames = sorted((render / "frames" / cid / d).glob(f"{cid}_{d}_*.png"))
            gif = out / f"{cid}_{d}.gif"
            imgs = []
            loaded = [Image.open(f).convert("RGBA") for f in frames]
            box = None
            for im in loaded:  # caixa comum a todos os quadros: o personagem não "pula" no GIF
                b = im.getbbox()
                box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
            box = (max(0, box[0] - 4), max(0, box[1] - 4), min(loaded[0].width, box[2] + 4), min(loaded[0].height, box[3] + 4))
            for im in loaded:
                im = im.crop(box)
                bg = Image.new("RGBA", im.size, (*BG, 255))
                bg.alpha_composite(im)
                imgs.append(bg.convert("P", palette=Image.ADAPTIVE, colors=255))
            imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=round(1000 / anim["fps"]), loop=0)
            atlas_src = ROOT / "exports" / slug / "atlases" / anim["directions"][d]["file"]
            shutil.copy2(atlas_src, out / "atlas" / atlas_src.name)
            per_dir[d] = {"status": status, "gif": f"showcase/{slug}/{gif.name}",
                          "atlas": f"showcase/{slug}/atlas/{atlas_src.name}", "smoke_failures": smoke_fail}
        clips[cid] = {
            "fps": anim["fps"], "frames": anim["frame_count"], "loop": anim["loop"], "category": anim.get("category", "locomotion"),
            "priority": anim.get("priority", 0), "interruptible_after": anim.get("interruptible_after", 0),
            "return_to": anim.get("return_to"), "held_frames": anim.get("held_frames", []), "phases": anim.get("phases", []),
            "events": anim.get("events", []), "duration_s": anim["duration_s"],
            "resolution": f"{anim['directions']['S']['frame_width']}×{anim['directions']['S']['frame_height']}",
            "checks": own, "scenario": scenario, "transitions": transitions, "directions": per_dir,
        }
    return {"slug": slug, "name": manifest["character_name"], "render_profile": manifest["render_profile"],
            "art_profile": manifest["art_profile"], "godot": (smoke or {}).get("godot"), "clips": clips,
            "state_scenarios": (states or {}).get("scenarios", [])}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"generated": date.today().isoformat(), "directions": DIRS,
            "catalog": [{"category": c, "action": a, "clip": k, "note": n} for c, a, k, n in CATALOG],
            "characters": [build(s) for s in sys.argv[1:]]}
    (OUT / "data.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    for ch in data["characters"]:
        counts = {}
        for clip in ch["clips"].values():
            for d in clip["directions"].values():
                counts[d["status"]] = counts.get(d["status"], 0) + 1
        print(ch["slug"], counts)


if __name__ == "__main__":
    main()
