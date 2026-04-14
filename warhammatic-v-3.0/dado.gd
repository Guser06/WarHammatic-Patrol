extends Node2D

@onready var animation=$AnimacionDado

func roll(res: int):
	animation.play("default")
	await get_tree().create_timer(2.0).timeout
	animation.stop()
	animation.frame = res
	await  get_tree().create_timer(3.0).timeout
