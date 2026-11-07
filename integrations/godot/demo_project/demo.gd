extends Node2D
## Cena de demonstração e teste E2E (GODOT-002).
## Sem argumentos: passeia por animações e direções. Com --capture <dir>: para cada clip, fixa
## cada frame, captura a tela e grava o que foi realmente desenhado para comparação externa.

const SECONDS_PER_DIRECTION := 0.9
const BACKGROUND := Color(0.23, 0.29, 0.26)

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var label: Label = $Label

var package := ""
var capture_dir := ""
var report := {"captures": [], "advanced": {}, "failures": []}


func _ready() -> void:
	RenderingServer.set_default_clear_color(BACKGROUND)
	var args := {}
	var user_args := OS.get_cmdline_user_args()
	for i in range(0, user_args.size() - 1, 2):
		args[user_args[i].trim_prefix("--")] = user_args[i + 1]
	package = args.get("package", _first_package())
	capture_dir = args.get("capture", "")
	if package.is_empty():
		label.text = "Nenhum personagem em res://characters. Exporte um pelo Studio."
		return
	sprite.sprite_frames = IcsCharacter.build_sprite_frames(package)
	IcsCharacter.apply_pivot(sprite, package)
	sprite.position = Vector2(320, 400)
	if capture_dir.is_empty():
		_tour()
	else:
		_capture_all()


func _first_package() -> String:
	var dirs := DirAccess.get_directories_at("res://characters")
	return "" if dirs.is_empty() else "res://characters".path_join(dirs[0])


func _tour() -> void:
	while true:
		for animation in ["idle", "walk", "run"]:
			for direction: String in IcsCharacter.DIRECTION_NAMES:
				var clip := "%s_%s" % [animation, direction]
				label.text = clip
				sprite.play(clip)
				await get_tree().create_timer(SECONDS_PER_DIRECTION).timeout


func _capture_all() -> void:
	for clip: StringName in sprite.sprite_frames.get_animation_names():
		await _measure_playback(clip)
		for frame in [0, sprite.sprite_frames.get_frame_count(clip) / 2]:
			sprite.animation = clip
			sprite.frame = frame
			sprite.pause()
			label.text = ""
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var name := "%s_%d.png" % [clip, frame]
			get_viewport().get_texture().get_image().save_png(capture_dir.path_join(name))
			report["captures"].append({"clip": clip, "frame": frame, "file": name,
				"origin": [sprite.position.x, sprite.position.y]})
	var file := FileAccess.open(capture_dir.path_join("report.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	get_tree().quit(0)


func _measure_playback(clip: StringName) -> void:
	var seen := {}
	sprite.play(clip)
	var duration := sprite.sprite_frames.get_frame_count(clip) / sprite.sprite_frames.get_animation_speed(clip)
	var elapsed := 0.0
	while elapsed < min(duration, 0.35):
		seen[sprite.frame] = true
		elapsed += get_process_delta_time()
		await get_tree().process_frame
	report["advanced"][clip] = seen.size()
	if seen.size() < 2:
		report["failures"].append("%s não avançou" % clip)
