import json
import socket
import threading
from WHmmatic_lib import Dados

clientes = []

def servidor_push():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 4242))
    server.listen(5)
    print("Esperando conexión de Godot...")
    
    client, addr = server.accept()
    clientes.append(client)
    print(f"Godot conectado desde {addr}")
    
    # Iniciar hilo para escuchar mensajes de Godot
    hilo = threading.Thread(target=escuchar_godot, args=(client,))
    hilo.daemon = True
    hilo.start()

def escuchar_godot(client):
    buffer = ""
    while True:
        try:
            data = client.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                mensaje, buffer = buffer.split("\n", 1)
                datos = json.loads(mensaje)
                procesar_mensaje_godot(datos, client)
        except Exception as e:
            print(f"Error recibiendo datos: {e}")
            break

def procesar_mensaje_godot(datos, client):
    tipo = datos.get("tipo")
    
    if tipo == "movimiento":
        miniatura = datos["miniatura"]
        pos_i = datos["pos_inicial"]
        pos_f = datos["pos_final"]
        print(f"Miniatura '{miniatura}' movida de {pos_i} a {pos_f}")
        
        # Aquí puedes conectarlo con tu lógica de WHmmatic_lib
        # Por ejemplo: validar si el movimiento es legal según las reglas
        
        respuesta = {"tipo": "ok", "miniatura": miniatura}
        notificar_a_godot(respuesta)

def notificar_a_godot(mensaje):
    payload = (json.dumps(mensaje) + "\n").encode("utf-8")
    for c in clientes:
        try:
            c.send(payload)
        except:
            clientes.remove(c)

def procesar_tiro_dados(n, caras, suma):
    resultado = Dados(n, caras, suma)
    respuesta = {
        "tipo": "resultado_dados",
        "es_suma": suma,
        "valores": [resultado] if suma else resultado,
        "total": resultado if suma else sum(resultado)
    }
    return respuesta

# --- Inicio ---
servidor_push()
m = {"Tipo": "Mensaje", "Contenido": "Hola mundo!"}
notificar_a_godot(m)