import json
import socket
import threading
from WHmmatic_lib import Dados

clientes = []

def procesar_tiro_dados(n, caras, suma):
    resultado = Dados(n, caras, suma)
    respuesta = {
        "tipo": "resultado_dados",
        "es_suma": suma,
        "valores": [resultado] if suma else resultado,
        "total": resultado if suma else sum(resultado)
    }
    return respuesta

def notificar_a_godot(mensaje):
    payload = json.dumps(mensaje).encode('utf-8')
    for c in clientes[:]:  # Copia de la lista para iterar seguro
        try:
            c.send(payload)
        except:
            clientes.remove(c)
    print("Info enviada")

def manejar_cliente(client, addr):
    """Se ejecuta en un hilo por cada cliente conectado."""
    print(f"Godot conectado desde {addr}")
    
    # Ahora sí hay un cliente — procesamos y enviamos
    m = procesar_tiro_dados(1, 6, False)
    notificar_a_godot(m)
    
    # Mantener el hilo vivo mientras el cliente esté conectado
    try:
        while True:
            data = client.recv(1024)
            if not data:
                break  # Godot cerró la conexión
            '''
            else:
                data = json.load(data)
                match data.tipo:
                    case "movimiento":
                        '''
    except:
        pass
    finally:
        clientes.remove(client)
        client.close()
        print(f"Cliente {addr} desconectado")

def servidor_push():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Evita "Address already in use"
    server.bind(("127.0.0.1", 4242))
    server.listen(5)
    print("Servidor escuchando en 127.0.0.1:4242...")
    
    while True:
        client, addr = server.accept()
        clientes.append(client)
        
        # Hilo dedicado por cliente
        hilo_cliente = threading.Thread(target=manejar_cliente, args=(client, addr))
        hilo_cliente.daemon = True
        hilo_cliente.start()

try:
    thread = threading.Thread(target=servidor_push)
    thread.daemon = True
    thread.start()

    print("Presiona Enter para salir...")
    input()  # Mantiene el proceso vivo
except KeyboardInterrupt:
    pass