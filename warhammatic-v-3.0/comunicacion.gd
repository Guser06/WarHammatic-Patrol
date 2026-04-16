extends Node

var socket = StreamPeerTCP.new()
var conectado = false

func _ready():
	socket.connect_to_host("127.0.0.1", 4242)
	
func _process(_delta):
	socket.poll()
	
	var estado = socket.get_status()
	if estado == StreamPeerTCP.STATUS_CONNECTED:
		if socket.get_available_bytes() > 0:
			var dato = socket.get_utf8_string(socket.get_available_bytes())
			_manejar_datos_de_python(dato)

func _manejar_datos_de_python(texto):
	print("info recibida")
	var datos = JSON.parse_string(texto)
	
	if datos.tipo == "resultado_dados":
		if datos.es_suma:
			print("El total es: ", datos.total)
		else:
			_ejecutar_animaciones_dados(datos.valores)

func _ejecutar_animaciones_dados(lista_valores):
	for valor in lista_valores:
		var dado_instancia = load("res://Escenas/dado.tscn").instantiate()
		get_parent().add_child(dado_instancia)
		
		dado_instancia.roll(valor)
		
		await get_tree().create_timer(5.0).timeout
