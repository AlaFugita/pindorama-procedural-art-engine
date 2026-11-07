class_name IcsAnimController
extends RefCounted
## Máquina de estados de animação do personagem, dirigida pelos metadados do pacote.
##
## Regras (vêm do manifesto, não do código):
## - locomoção (idle/walk/run) tem prioridade 0 e segue o movimento;
## - uma ação (priority > 0, sem laço) toca até o fim e volta para ``return_to``
##   (ou para walk/run se o personagem ainda se move);
## - pedido de prioridade MAIOR interrompe a qualquer momento;
## - pedido de prioridade IGUAL ou movimento só corta a ação a partir de ``interruptible_after``;
##   antes disso, um pedido de ação fica guardado (um só) e toca em seguida;
## - mudar de direção durante a ação troca o clip da direção sem reiniciar o quadro;
## - ``return_to`` vazio = estado terminal (morte): nada mais é aceito.
## O tempo é avançado por ``step(delta)``, então o teste é determinístico.

var clips := {}  # nome -> metadados do manifesto
var state := "idle"
var direction := "S"
var time := 0.0
var frame := 0
var moving := false
var running := false
var queued := ""
var terminal := false
var history: Array[String] = []


func _init(animations: Array) -> void:
	for animation: Dictionary in animations:
		clips[animation["animation"]] = animation


func clip_name() -> String:
	return "%s_%s" % [state, direction]


func is_action(name: String) -> bool:
	return not bool(clips[name]["loop"])


func locomotion() -> String:
	if not moving:
		return "idle"
	return "run" if running and clips.has("run") else "walk"


func set_motion(vector: Vector2, run := false) -> void:
	moving = vector.length() > 0.01
	running = run
	if moving:
		direction = IcsCharacter.vector_to_direction(vector)
	if terminal:
		return
	if is_action(state):
		if moving and frame >= int(clips[state]["interruptible_after"]):
			_enter(locomotion())
		return
	_enter(locomotion())


func request(name: String) -> bool:
	if terminal or not clips.has(name):
		return false
	var current := int(clips[state]["priority"])
	var wanted := int(clips[name]["priority"])
	if not is_action(state) or wanted > current:
		_enter(name)
		return true
	if wanted == current and frame >= int(clips[state]["interruptible_after"]):
		_enter(name)
		return true
	if wanted == current:
		queued = name
	return false


func step(delta: float) -> void:
	time += delta
	var meta: Dictionary = clips[state]
	var count := int(meta["frame_count"])
	var raw := int(floor(time * float(meta["fps"]) + 1e-6))
	if bool(meta["loop"]):
		frame = raw % count
		return
	if raw < count:
		frame = raw
		return
	frame = count - 1
	if meta["return_to"] == null:
		terminal = true
		return
	if queued != "":
		var next := queued
		queued = ""
		_enter(next)
	elif moving:
		_enter(locomotion())
	else:
		_enter(str(meta["return_to"]))


func _enter(name: String) -> void:
	if name == state and not is_action(name):
		return
	state = name
	time = 0.0
	frame = 0
	terminal = false
	history.append(name)
