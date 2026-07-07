extends Node

const URL_status = "http://127.0.0.1:8000/status"
const URL_post_Army = "http://127.0.0.1:8000/create_army"
const URL_WS = "ws://127.0.0.1:8000/ws"

##Variables que deberán ser definidas en menú
var id = 1 #Asignado en función de host/cliente
var ej_elegido = '1st & 9th' #Elegido mediante botones en menú

##Variables de comunicación WebSocket
var socket = WebSocketPeer.new()
var ws_conectado = false

# Called when the node enters the scene tree for the first time.
func _ready():
	$HTTPRequest.request_completed.connect(_on_request_completed)
	$HTTPRequest.request(URL_status)
	## var headers = ["Content-Type: application/json"]
	## var army_json = JSON.stringify({"player_id": id, "army_name": ej_elegido})
	## await get_tree().create_timer(5.0).timeout
	## $HTTPRequest.request(URL_post_Army, headers, HTTPClient.METHOD_POST, army_json)
	
	var error = socket.connect_to_url(URL_WS)
	if error == OK:
		print("Intentando conectar al websocket")
	else:
		print("Conexión a websocket fallida ", error)

func _process(_delta):
	# Es vital llamar a poll() en cada frame para que el socket procese los datos internos
	socket.poll()
	
	var estado = socket.get_status()
	
	if estado == WebSocketPeer.STATE_OPEN:
		if not ws_conectado:
			print("¡Conectado exitosamente al WebSocket de Python!")
			ws_conectado = true
			# Ejemplo: Mandar un paquete inicial apenas nos conectamos
			enviar_datos_ws({"accion": "login", "player_id": 1})
		
		# Verificar si Python nos envió algo
		while socket.get_available_packet_count() > 0:
			var paquete = socket.get_packet()
			var texto = paquete.get_string_from_utf8()
			_on_datos_ws_recibidos(texto)
			
	elif estado == WebSocketPeer.STATE_CLOSED:
		if ws_conectado:
			print("El WebSocket se ha cerrado.")
			ws_conectado = false

# Función para enviar acciones (como mover un Individuo o tirar Dados)
func enviar_datos_ws(diccionario_datos: Dictionary):
	if socket.get_status() == WebSocketPeer.STATE_OPEN:
		var json_texto = JSON.stringify(diccionario_datos)
		socket.put_packet(json_texto.to_utf8_buffer())
	else:
		print("Error: No se pudo enviar datos, el WebSocket está cerrado.")

# Aquí reaccionas a lo que Python decida (Sea privado o broadcast)
func _on_datos_ws_recibidos(texto_json):
	var datos = JSON.parse_string(texto_json)
	print("Mensaje del Servidor: ", datos)
	
	# Aquí disparas la lógica visual de tu juego
	if datos.has("message"):
		print("Alerta del sistema: ", datos["message"])

func _on_request_completed(result, response_code, headers, body):
	print("Codigo de respuesta: ", response_code)
	print("Respuesta cruda: ", body)
	print(headers)
	
	var json = JSON.parse_string(body.get_string_from_utf8())
	print(json)
