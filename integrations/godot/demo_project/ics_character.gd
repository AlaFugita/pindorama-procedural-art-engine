class_name IcsCharacter
extends RefCounted
## Carrega um pacote exportado pelo Isometric Character Studio em um SpriteFrames.
## Não depende do aplicativo gerador em tempo de execução.

const DIRECTION_NAMES: PackedStringArray = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


## Direção canônica para um vetor de jogo em que +X = leste e +Y = sul (padrão 2D do Godot).
static func vector_to_direction(vector: Vector2) -> String:
	assert(vector != Vector2.ZERO)
	var heading := fposmod(rad_to_deg(atan2(vector.x, -vector.y)), 360.0)
	return DIRECTION_NAMES[int(floor((heading + 22.5) / 45.0)) % 8]


static func read_animations(package_dir: String) -> Array:
	var path := package_dir.path_join("metadata/animations.json")
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not (data is Dictionary) or not data.has("animations"):
		push_error("metadados inválidos: " + path)
		return []
	return data["animations"]


static func build_sprite_frames(package_dir: String) -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	for animation: Dictionary in read_animations(package_dir):
		for direction: String in animation["direction_order"]:
			var entry: Dictionary = animation["directions"][direction]
			var clip := StringName("%s_%s" % [animation["animation"], direction])
			var texture: Texture2D = load(package_dir.path_join("atlases").path_join(entry["file"]))
			frames.add_animation(clip)
			frames.set_animation_speed(clip, animation["fps"])
			frames.set_animation_loop_mode(
				clip,
				SpriteFrames.LOOP_LINEAR if animation["loop"] else SpriteFrames.LOOP_NONE
			)
			for rect: Dictionary in entry["frames"]:
				var region := AtlasTexture.new()
				region.atlas = texture
				region.region = Rect2(rect["x"], rect["y"], rect["w"], rect["h"])
				# Atlas recortado: a margem devolve o tamanho e a posição do quadro cheio.
				var ox: float = rect.get("ox", 0)
				var oy: float = rect.get("oy", 0)
				region.margin = Rect2(ox, oy, entry["frame_width"] - rect["w"], entry["frame_height"] - rect["h"])
				frames.add_frame(clip, region)
	return frames


## Posiciona o sprite de modo que o nó fique exatamente sobre o ponto de apoio.
static func apply_pivot(sprite: AnimatedSprite2D, package_dir: String) -> void:
	var animation: Dictionary = read_animations(package_dir)[0]
	var pivot: Dictionary = animation["directions"]["S"]["pivot"]
	sprite.centered = false
	sprite.offset = Vector2(-pivot["x"], -pivot["y"])
