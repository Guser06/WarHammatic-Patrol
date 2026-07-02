from fastapi import FastAPI, Websocket
from pydantic import BaseModel
from WHmmatic_lib import *

conexiones = {}

app = FastAPI()

class CreateArmyRequest(BaseModel):
    n

@app.websocket("/ws")
async def websocket_connection(ws: Websocket):
    await ws.accept()
    conexiones.update({f"{len(conexiones.items())}": ws})
    try:
        while True:
            datos = await ws.receive_json()
            respuesta = procesar_request(datos)
            if respuesta["privado"]:
                await ws.send(respuesta)
            else:
                for con in conexiones.values():
                    await con.send(respuesta)
    except:
        conexiones.remove(ws)
        for con in conexiones.values():
            try:
                await con.send(
                    {"message": "Un jugador se ha desconectado"}
                    )
            except:
                conexiones.remove(con)
            
def procesar_request(datos: dict):
    match datos["type"]:
        case "datasheet":
            pass
        case "move":
            pass
        case "advance":
            pass
        case "fallback":
            pass
        case "select":
            pass
        case "shoot":
            pass
        case "charge":
            pass
        case "fight":
            pass
        case "stratagem":
            pass
        case "begin_action":
            pass