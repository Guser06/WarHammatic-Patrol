extends CharacterBody2D

var accel = 1.5

func _process(delta: float) -> void:
	var direccion_x = Input.get_axis("Left", "Right")
	var direccion_y = Input.get_axis("Up", "Down")
	velocity.x = (abs(velocity.x)*direccion_x) + (accel*direccion_x)
	velocity.y = (abs(velocity.y)*direccion_y) + (accel*direccion_y)
	move_and_slide()
