extends Node

var socket = StreamPeerTCP.new()
var conectado = false

func _ready():
	socket.connect_to_host("127.0.0.1", 4242)

func _process(_delta):
	socket.poll()
	var estado = socket.get_status()
	conectado = (estado == StreamPeerTCP.STATUS_CONNECTED)
	
	if conectado and socket.get_available_bytes() > 0:
		var dato = socket.get_utf8_string(socket.get_available_bytes())
		print("Respuesta del servidor: ", dato)

func enviar(texto: String):
	if conectado:
		socket.put_data(texto.to_utf8_buffer())
	else:
		print("No hay conexión con el servidor Python")
