extends SceneTree
## GODOT-003: transições de estado com o pacote real (metadados + SpriteFrames importados).
## Uso: godot --headless --path <proj> --script res://state_test.gd -- --package res://x --result r.json

var failures: Array[String] = []
var scenarios: Array[Dictionary] = []


func _init() -> void:
	var args := {}
	var raw := OS.get_cmdline_user_args()
	for i in range(0, raw.size() - 1, 2):
		args[raw[i].trim_prefix("--")] = raw[i + 1]
	var package: String = args["package"]
	var animations := IcsCharacter.read_animations(package)
	var frames := IcsCharacter.build_sprite_frames(package)
	_run_all(animations, frames)
	var file := FileAccess.open(args["result"], FileAccess.WRITE)
	file.store_string(JSON.stringify({"scenarios": scenarios, "failures": failures}, "  "))
	file.close()
	quit(0 if failures.is_empty() else 1)


func _scenario(name: String, actions: Array, ok: bool, detail: String) -> void:
	scenarios.append({"name": name, "actions": actions, "status": "PASS" if ok else "FAIL", "detail": detail})
	if not ok:
		failures.append("%s: %s" % [name, detail])


func _new(animations: Array) -> IcsAnimController:
	return IcsAnimController.new(animations)


func _run_for(c: IcsAnimController, seconds: float, fps := 60.0) -> Array:
	var seen: Array = []
	var steps := int(round(seconds * fps))
	for i in steps:
		c.step(1.0 / fps)
		seen.append([c.state, c.direction, c.frame])
	return seen


func _run_all(animations: Array, frames: SpriteFrames) -> void:
	var meta := {}
	for a: Dictionary in animations:
		meta[a["animation"]] = a
	# 1. Cada clip: SpriteFrames tem o clip nas 8 direções, mesma contagem, FPS e laço do manifesto;
	#    a sequência tocada em tempo de jogo passa por todos os quadros, em ordem, sem pular nem repetir.
	for name: String in meta:
		var a: Dictionary = meta[name]
		var problems: Array[String] = []
		for d: String in IcsCharacter.DIRECTION_NAMES:
			var clip := StringName("%s_%s" % [name, d])
			if not frames.has_animation(clip):
				problems.append("sem %s" % clip)
				continue
			if frames.get_frame_count(clip) != int(a["frame_count"]):
				problems.append("%s: quadros" % clip)
			if not is_equal_approx(frames.get_animation_speed(clip), float(a["fps"])):
				problems.append("%s: fps" % clip)
		var c := _new(animations)
		if bool(a["loop"]):
			c._enter(name)
		else:
			c.request(name)
		var order: Array = []
		var duration := float(a["frame_count"]) / float(a["fps"])
		for s in _run_for(c, duration - 0.5 / float(a["fps"]), float(a["fps"]) * 4.0):
			if s[0] == name and (order.is_empty() or order[-1] != s[2]):
				order.append(s[2])
		var expected := range(int(a["frame_count"]))
		if order != expected:
			problems.append("sequência %s" % [order])
		_scenario("clip:%s" % name, [name], problems.is_empty(), "; ".join(problems) if problems else
			"%d quadros a %d fps (%.2fs), 8 direções no SpriteFrames, sequência completa" % [a["frame_count"], a["fps"], duration])
	if not meta.has("attack_melee"):
		return
	# 2. Locomoção segue o movimento e a direção.
	var c := _new(animations)
	c.set_motion(Vector2(1, 0))
	var walk_ok := c.state == "walk" and c.direction == "E"
	c.set_motion(Vector2(1, 1), true)
	var run_ok := c.state == "run" and c.direction == "SE"
	c.set_motion(Vector2.ZERO)
	_scenario("idle→walk→run→idle", ["idle", "walk", "run"], walk_ok and run_ok and c.state == "idle",
		"histórico %s" % [c.history])
	# 3. Ação a partir de idle volta para idle no tempo certo.
	for action: String in ["attack_melee", "cast", "interact", "hurt"]:
		if not meta.has(action):
			continue
		c = _new(animations)
		c.request(action)
		var duration := float(meta[action]["frame_count"]) / float(meta[action]["fps"])
		_run_for(c, duration - 0.02)
		var still := c.state == action
		_run_for(c, 0.05)
		_scenario("%s: idle→ação→idle" % action, [action], still and c.state == "idle",
			"dura %.2fs e volta para %s" % [duration, c.state])
	# 4. Andar + atacar: a ação toca e, terminando, volta a andar (ainda em movimento).
	c = _new(animations)
	c.set_motion(Vector2(0, 1))
	c.request("attack_melee")
	var attacked := c.state == "attack_melee"
	_run_for(c, 1.0)
	_scenario("andar + atacar", ["walk", "attack_melee"], attacked and c.state == "walk", "termina em %s" % c.state)
	# 5. Correr + atacar: volta a correr.
	c = _new(animations)
	c.set_motion(Vector2(-1, 0), true)
	c.request("attack_melee")
	_run_for(c, 1.0)
	_scenario("correr + atacar", ["run", "attack_melee"], c.state == "run", "termina em %s" % c.state)
	# 6. Mudar de direção no meio do ataque: troca a direção sem reiniciar o quadro.
	c = _new(animations)
	c.request("attack_melee")
	_run_for(c, 2.5 / 12.0)
	var before := c.frame
	var dir_before := c.direction
	c.direction = "W"
	var kept := c.state == "attack_melee" and c.frame == before and dir_before != "W" and c.clip_name() == "attack_melee_W"
	_scenario("atacar e virar", ["attack_melee"], kept, "quadro %d mantido, clip %s" % [c.frame, c.clip_name()])
	# 7. Magia + movimento: antes do quadro interruptível o movimento não corta; depois, corta.
	c = _new(animations)
	c.request("cast")
	_run_for(c, 2.0 / 12.0)
	c.set_motion(Vector2(0, -1))
	var held := c.state == "cast"
	_run_for(c, (float(meta["cast"]["interruptible_after"]) - 1.0) / 12.0)
	c.set_motion(Vector2(0, -1))
	_scenario("magia + movimento", ["cast", "walk"], held and c.state == "walk",
		"preparo protegido; corta a recuperação a partir do quadro %d" % meta["cast"]["interruptible_after"])
	# 8. Interagir em movimento: a interação começa (para o movimento), depois retoma o andar.
	c = _new(animations)
	c.set_motion(Vector2(1, 0))
	c.request("interact")
	var started := c.state == "interact"
	_run_for(c, 1.0)
	_scenario("interagir em movimento", ["walk", "interact"], started and c.state == "walk", "termina em %s" % c.state)
	# 9. Dano interrompe ataque a qualquer momento e depois volta para idle.
	c = _new(animations)
	c.request("attack_melee")
	_run_for(c, 1.5 / 12.0)
	var cut := c.request("hurt") and c.state == "hurt"
	_run_for(c, 1.0)
	_scenario("dano interrompe ataque", ["attack_melee", "hurt"], cut and c.state == "idle", "histórico %s" % [c.history])
	# 10. Ataque pedido durante o dano é recusado (prioridade menor).
	c = _new(animations)
	c.request("hurt")
	var refused := not c.request("attack_melee") and c.state == "hurt"
	_scenario("ataque durante dano", ["hurt", "attack_melee"], refused, "estado %s" % c.state)
	# 11. Ataque repetido: guardado antes do quadro interruptível e tocado em seguida (combo de 2).
	c = _new(animations)
	c.request("attack_melee")
	_run_for(c, 1.0 / 12.0)
	c.request("attack_melee")
	_run_for(c, 8.0 / 12.0 - 1.0 / 12.0 + 0.01)
	var chained := c.state == "attack_melee" and c.history.count("attack_melee") == 2
	_scenario("dois ataques seguidos", ["attack_melee"], chained, "histórico %s" % [c.history])
	# 12. Morte interrompe tudo, termina parada no último quadro e não aceita mais nada.
	if meta.has("death"):
		c = _new(animations)
		c.set_motion(Vector2(1, 0), true)
		c.request("cast")
		var died := c.request("death")
		_run_for(c, 2.0)
		var last := c.frame == int(meta["death"]["frame_count"]) - 1
		var locked := not c.request("attack_melee") and not c.request("hurt")
		c.set_motion(Vector2(0, 1))
		_scenario("morte é terminal", ["death"], died and last and locked and c.state == "death",
			"quadro final %d, estado %s" % [c.frame, c.state])
