"""Escreve docs/ANIMATION_VALIDATION.md a partir de docs/showcase/data.json (mesmos dados da página)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "docs/showcase/data.json").read_text(encoding="utf-8"))
DIRS = data["directions"]
out = []
w = out.append

w("# Validação das animações\n")
w(f"**Gerado em:** {data['generated']} por `scripts/build_animation_report.py`, a partir dos testes executados.")
w("**Página:** [animations.html](../animations.html), com filtros, as 8 direções lado a lado e os detalhes de cada animação.\n")
w("## Como o status é calculado\n")
w("| Status | Regra |\n|---|---|")
w("| PASS | Gates do clip aprovados (G5: IK, contato, deslizamento, laço, chão; G6: imagem) **e** o Godot importou, tocou na velocidade e na sequência certas **e** os cenários de estado com essa ação passaram |")
w("| WARN | Funciona, com ressalva medida (ex.: quadros repetidos acidentais, coxa a mais de 15 mm da túnica) |")
w("| FAIL | Algum check do clip falhou nos gates ou no Godot |")
w("| MISSING | Ação do catálogo sem clip implementado |")
w("| NOT TESTED | Clip existe, mas o Godot não rodou para esse personagem |\n")
w("Um GIF existir **não** muda o status.\n")

for ch in data["characters"]:
    w(f"## {ch['name']} (`{ch['slug']}`, {ch['render_profile']})\n")
    w(f"Godot: {ch['godot']}\n")
    w("### Matriz de cobertura\n")
    w("| Categoria | Ação | Clip | " + " | ".join(DIRS) + " |")
    w("|---|---|---|" + "---|" * len(DIRS))
    for item in data["catalog"]:
        clip = ch["clips"].get(item["clip"]) if item["clip"] else None
        cells = [clip["directions"][d]["status"] if clip else "MISSING" for d in DIRS]
        w(f"| {item['category']} | {item['action']} | `{item['clip'] or '—'}` | " + " | ".join(cells) + " |")
    w("")
    w("### Clips implementados\n")
    w("| Clip | Categoria | FPS | Quadros | Duração | Laço | Prioridade | Interrompível | Volta para | Fases | Problemas |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for cid, c in ch["clips"].items():
        phases = ", ".join(f"{p['name']} {p['start_frame']}–{p['end_frame']}" for p in c["phases"]) or "—"
        problems = "; ".join(f"{k['id']}: {k['detail']}" for k in c["checks"] if k["status"] != "PASS") or "—"
        w(f"| `{cid}` | {c['category']} | {c['fps']} | {c['frames']} | {c['duration_s']:.2f}s | {'sim' if c['loop'] else 'não'} | "
          f"{c['priority']} | {c['interruptible_after']} | {c['return_to'] or 'terminal'} | {phases} | {problems} |")
    w("")
    w("### Cenários de estado executados no Godot (GODOT-003)\n")
    w("| Cenário | Ações | Status | Resultado |\n|---|---|---|---|")
    for s in ch["state_scenarios"]:
        w(f"| {s['name']} | {', '.join(s['actions'])} | {s['status']} | {s['detail']} |")
    w("")

w("## Testes do Godot realizados\n")
w("| ID | O que verifica | Onde |\n|---|---|---|")
w("| GODOT-001 | Importação: cada clip nas 8 direções, contagem de quadros, FPS e modo de laço iguais ao manifesto; pixels importados idênticos ao PNG; alpha preservado; região de cada quadro | `smoke_test.gd` (headless) |")
w("| GODOT-002 | Reprodução real com janela: `AnimatedSprite2D` toca os clips, a tela capturada bate com o quadro esperado (posição e pivô) | captura + `godot_bridge.compare_captures` |")
w("| GODOT-003 | Máquina de estados com o pacote real: sequência de quadros completa e em ordem no tempo de jogo, duração, retorno ao estado certo, andar/correr + atacar, virar no meio da ação, magia + movimento, interagir em movimento, dano interrompendo ataque, ataque recusado durante o dano, dois ataques em fila, morte terminal | `state_test.gd` + `ics_anim_controller.gd` |")
w("")
w("## Regras de prioridade e interrupção (implementadas em `IcsAnimController`)\n")
w("- Locomoção (idle, walk, run): prioridade 0; segue o movimento e a direção.")
w("- Ação sem laço (ataque, magia, interação): prioridade 10; toca até o fim e volta para `return_to`, ou para walk/run se ainda há movimento.")
w("- Prioridade **maior** interrompe a qualquer momento: dano (20) corta ação; morte (100) corta tudo.")
w("- Movimento ou ação de **mesma** prioridade só corta a partir de `interruptible_after`. Antes disso, o pedido de ação fica numa fila de um item, que gera o combo de 2.")
w("- Mudar de direção durante a ação troca o clip da direção **sem reiniciar** o quadro.")
w("- Morte é terminal: `return_to` vazio; nada mais é aceito.")
w("- A movimentação do jogo não é bloqueada pelo controlador. O jogo deve parar o deslocamento durante ações de prioridade ≥ 10 (as ações são `in_place`).\n")

w("## Animações ausentes (MISSING)\n")
seen = set()
for item in data["catalog"]:
    if item["clip"] is None and item["action"] not in seen:
        seen.add(item["action"])
        w(f"- **{item['category']} / {item['action']}**" + (f": {item['note']}" if item["note"] else ""))
w("")
w("## Problemas encontrados\n")
w("1. **Magia (`cast`) em WARN:** a coxa sai até 15,8 mm da túnica no lançamento (limite de aviso: 15 mm). Invisível nas vistas frontais, mas medido. Abrir a barra da túnica ou reduzir a inclinação.")
w("2. **Idle em WARN (IMG-005):** 3 quadros repetidos por direção. São fases simétricas do ciclo de respiração (cos 2θ). É uma repetição acidental, não marcada em `held_frames`.")
w("3. **Corrigidos nesta etapa:**")
w("   - morte com o cajado 82 mm abaixo do chão, achada pelo ANI-005;")
w("   - quadro inicial = final em todas as ações (engasgo na volta ao idle);")
w("   - dano começando em pose neutra.")
w("4. **Sem bloqueio de deslocamento:** as ações são `in_place`. O jogo precisa travar o movimento durante a ação; isso é regra documentada, não aplicada pelo pacote.")
w("5. **Mesmo clip para variações de interação** (coletar, NPC, usar): marcadas como MISSING; hoje só existe `interact` genérico.\n")
w("## Plano de correção priorizado\n")
w("| Pri. | Item | Por quê | Esforço |\n|---|---|---|---|")
w("| P1 | Ajustar `cast` (coxa) e marcar ou corrigir as repetições do idle | Zerar os WARN atuais | Baixo |")
w("| P1 | `WeaponProfile`: empunhadura e clips por tipo de arma (espada, arco, lança) | Arco não pode usar ataque de cajado (§11.2) | Médio |")
w("| P1 | Ranged: `aim`, `shoot`, `throw` com evento de projétil | Combate à distância inteiro está MISSING | Médio |")
w("| P2 | `stunned` (laço), `respawn` (ação de entrada) | Estados de combate comuns em MMORPG | Baixo |")
w("| P2 | Variações de interação: `pickup` (abaixar), `talk`, `use_item` | Interações distintas no jogo | Baixo |")
w("| P2 | Root motion vertical: `jump`, `fall`, `land` | Exige mudar o contrato `in_place` e o validador de contato | Alto |")
w("| P3 | Combos com clips próprios (ataque 2 e 3) | Hoje o combo repete o mesmo clip | Médio |")
w("| P3 | Integração com o movimento do jogo (Pindorama Engine): travar deslocamento por prioridade | Hoje é regra documentada | Médio |")
(ROOT / "docs/ANIMATION_VALIDATION.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("ok", len(out), "linhas")
