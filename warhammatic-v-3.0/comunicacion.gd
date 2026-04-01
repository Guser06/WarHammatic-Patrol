extends Node

var socket = StreamPeerTCP.new()
var conectado = false

func _ready():
	socket.connect_to_host("127.0.0.1", 4242)

func _process(_delta):
	socket.poll() # Actualiza el estado del socket
	
	var estado = socket.get_status()
	if estado == StreamPeerTCP.STATUS_CONNECTED:
		if socket.get_available_bytes() > 0:
			var dato = socket.get_utf8_string(socket.get_available_bytes())
			_manejar_datos_de_python(dato)

# En tu script de Godot
func _manejar_datos_de_python(texto):
	var datos = JSON.parse_string(texto)
	
	if datos.tipo == "resultado_dados":
		if datos.es_suma:
			print("El total es: ", datos.total)
		# Mostrar directamente el total en una etiqueta UI
		else:
			_ejecutar_animaciones_dados(datos.valores)

func _ejecutar_animaciones_dados(lista_valores):
	for valor in lista_valores:
		# Suponiendo que tienes una escena 'Dado.tscn' con una animación
		var dado_instancia = load("res://Dado.tscn").instantiate()
		add_child(dado_instancia)
		
		# Le pasamos el valor al dado para que su animación termine en el número correcto
		dado_instancia.lanzar(valor) 
		
		# Opcional: un pequeño retraso entre dados para que no salgan todos al mismo tiempo
		await get_tree().create_timer(0.2).timeout
