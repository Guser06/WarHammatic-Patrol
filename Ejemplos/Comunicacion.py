import json
import socket
import threading
from WHmmatic_lib import Dados

# Lista para manejar conexiones (por si luego quieres multijugador)
clientes = []

def servidor_push():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 4242))
    server.listen(5)
    
    client, addr = server.accept()
    clientes.append(client)
    print(clientes)
    print(f"Godot conectado desde {addr}")

socket.socket.

def procesar_entrada():
    for cliente in clientes:
        if cliente.

# Función que puedes llamar desde cualquier parte de tu lógica de 6k líneas
def notificar_a_godot(mensaje):
    payload = json.dumps(mensaje).encode('utf-8')
    for c in clientes:
        try:
            c.send(payload)
        except:
            clientes.remove(c)
    print("Info enviada")

def procesar_tiro_dados(n, caras, suma):
    resultado = Dados(n, caras, suma)
    
    # Preparamos un paquete de datos para Godot
    # Usamos una estructura consistente para que Godot siempre sepa qué esperar
    respuesta = {
        "tipo": "resultado_dados",
        "es_suma": suma,
        "valores": [resultado] if suma else resultado, # Siempre mandamos una lista para facilitar el código en Godot
        "total": resultado if suma else sum(resultado)
    }
    return respuesta

thread = threading.Thread(target=servidor_push, args=())
m = procesar_tiro_dados(1, 6, False)
notificar_a_godot(m)