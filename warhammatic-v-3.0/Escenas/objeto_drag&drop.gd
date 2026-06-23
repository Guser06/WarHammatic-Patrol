extends Area2D

var dragging = false
var offset = Vector2.ZERO
var posicion_inicial = Vector2.ZERO

func _ready():
	posicion_inicial = global_position

func _input_event(_viewport, event, _shape_idx):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			dragging = true
			posicion_inicial = global_position
			offset = get_global_mouse_position() - global_position

func _input(event):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if not event.pressed and dragging:
			dragging = false
			_al_soltar()

func _process(_delta):
	if dragging:
		var screen_size = get_viewport_rect().size
		var sprite = $Sprite2D
		var sprite_size = sprite.texture.get_size() * sprite.scale
		var half = sprite_size / 2
		var raw_pos = get_global_mouse_position() - offset
		position = Vector2(
			clamp(raw_pos.x, half.x, screen_size.x - half.x),
			clamp(raw_pos.y, half.y, screen_size.y - half.y)
		)

func _al_soltar():
	# Obtener todas las áreas que están chocando con esta miniatura
	var colisiones = get_overlapping_areas()
	
	if colisiones.size() > 0:
		# Hay colisión con otra miniatura, regresar
		print("Posición inválida (regresa a posición inicial)")
		position = posicion_inicial
	else:
		# Posición válida, mandar al servidor
		print("Movimiento válido")
		_mandar_movimiento(posicion_inicial, global_position)

func _mandar_movimiento(pos_inicial: Vector2, pos_final: Vector2):
	var datos = {
		"tipo": "movimiento",
		"miniatura": name,  # usa el nombre del nodo como ID
		"pos_inicial": {"x": pos_inicial.x, "y": pos_inicial.y},
		"pos_final": {"x": pos_final.x, "y": pos_final.y}
	}
	var json_str = JSON.stringify(datos) + "\n"
	
	# Buscar el nodo servidor en la escena
	var servidor = get_node("/root/Mundo/Servidor")
	if servidor:
		servidor.enviar(json_str)
