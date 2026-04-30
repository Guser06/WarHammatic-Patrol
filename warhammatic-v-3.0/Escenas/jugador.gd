extends CharacterBody2D
@onready var Cam = $Camera2D
@export var zoom_speed: float = 0.1
@export var min_zoom: float = 0.5
@export var max_zoom: float = 3.0
var accel = 1.5

func _process(delta: float) -> void:
	var direccion_x = Input.get_axis("Left", "Right")
	var direccion_y = Input.get_axis("Up", "Down")
	velocity.x = (abs(velocity.x)*direccion_x) + (accel*direccion_x)
	velocity.y = (abs(velocity.y)*direccion_y) + (accel*direccion_y)
	##Cam.zoom += Vector2(Input.get_axis("ScrollDown", "ScrollUp")*20, Input.get_axis("ScrollDown", "ScrollUp")*20)
	##Cam.zoom = Cam.zoom.clamp(Vector2(0.5, 0.5), Vector2(2.0, 2.0))
	move_and_slide()

func _unhandled_input(event):
	if event.is_action_pressed("ScrollDown"):
		Cam.zoom -= Vector2(zoom_speed, zoom_speed)
	if event.is_action_pressed("ScrollUp"):
		Cam.zoom += Vector2(zoom_speed, zoom_speed)
	Cam.zoom = Cam.zoom.clamp(Vector2(min_zoom, min_zoom), Vector2(max_zoom, max_zoom))
