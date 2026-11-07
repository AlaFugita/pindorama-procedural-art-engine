extends SceneTree
## Teste headless (GODOT-001). Uso:
## godot --headless --path <proj> --script res://smoke_test.gd -- --package res://x --result r.json


func _init() -> void:
	var args := _parse_args()
	var report := run_checks(args["package"])
	var file := FileAccess.open(args["result"], FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	quit(0 if report["failures"].is_empty() else 1)


func _parse_args() -> Dictionary:
	var result := {}
	var args := OS.get_cmdline_user_args()
	for i in range(0, args.size() - 1, 2):
		result[args[i].trim_prefix("--")] = args[i + 1]
	return result


func run_checks(package: String) -> Dictionary:
	var failures: Array[String] = []
	var animations := IcsCharacter.read_animations(package)
	var frames := IcsCharacter.build_sprite_frames(package)
	var total_frames := 0
	for animation: Dictionary in animations:
		for direction: String in IcsCharacter.DIRECTION_NAMES:
			var clip := StringName("%s_%s" % [animation["animation"], direction])
			if not frames.has_animation(clip):
				failures.append("clip ausente: %s" % clip)
				continue
			var entry: Dictionary = animation["directions"][direction]
			var count := frames.get_frame_count(clip)
			total_frames += count
			if count != int(animation["frame_count"]):
				failures.append("%s: %d frames" % [clip, count])
			if frames.get_animation_speed(clip) != float(animation["fps"]):
				failures.append("%s: fps" % clip)
			if (frames.get_animation_loop_mode(clip) == SpriteFrames.LOOP_LINEAR) != animation["loop"]:
				failures.append("%s: loop" % clip)
			_check_pixels(package, entry, clip, frames, failures)
	var vectors := {
		"N": Vector2(0, -1), "NE": Vector2(1, -1), "E": Vector2(1, 0), "SE": Vector2(1, 1),
		"S": Vector2(0, 1), "SW": Vector2(-1, 1), "W": Vector2(-1, 0), "NW": Vector2(-1, -1),
	}
	for name: String in vectors:
		if IcsCharacter.vector_to_direction(vectors[name]) != name:
			failures.append("direção %s mapeada errado" % name)
	return {
		"godot": Engine.get_version_info()["string"],
		"animations": animations.size(),
		"clips": frames.get_animation_names().size(),
		"frames": total_frames,
		"failures": failures,
	}


func _check_pixels(
	package: String, entry: Dictionary, clip: StringName, frames: SpriteFrames, failures: Array[String]
) -> void:
	var atlas_path: String = package.path_join("atlases").path_join(entry["file"])
	var imported: Image = (load(atlas_path) as Texture2D).get_image()
	var raw := Image.load_from_file(ProjectSettings.globalize_path(atlas_path))
	if imported == null or raw == null:
		failures.append("%s: textura não carregou" % clip)
		return
	if imported.get_size() != Vector2i(entry["atlas_width"], entry["atlas_height"]):
		failures.append("%s: tamanho importado %s" % [clip, imported.get_size()])
		return
	imported.convert(Image.FORMAT_RGBA8)
	raw.convert(Image.FORMAT_RGBA8)
	if not imported.has_alpha() or not imported.detect_alpha():
		failures.append("%s: sem alpha após importar" % clip)
	if imported.get_data() != raw.get_data():
		failures.append("%s: pixels mudaram na importação" % clip)
	for rect: Dictionary in entry["frames"]:
		var frame: AtlasTexture = frames.get_frame_texture(clip, int(rect["index"]))
		if frame.region != Rect2(rect["x"], rect["y"], rect["w"], rect["h"]):
			failures.append("%s: região do frame %s" % [clip, rect["index"]])
		if imported.get_pixel(int(rect["x"]), int(rect["y"])).a != 0.0:
			failures.append("%s: canto do frame %s opaco" % [clip, rect["index"]])
