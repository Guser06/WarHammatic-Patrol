import uvicorn
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import WHmmatic_lib as whlib 
from pathlib import Path
import json

conexiones = {}

app = FastAPI()

class CreateArmyRequest(BaseModel):
    player_id: int
    army_name: str

@app.get('/')
async def root():
    return {'message': 'test, hello from ipv6'}


@app.get("/status")
async def get_status():
    return {"message": "API is running"}

@app.post("/create_army")
async def create_army(request: CreateArmyRequest):
    if request.army_name in whlib.DISPONIBLE:
        filepath = None
        match request.army_name:
            case 'Tyranids patrol':
                filepath = Path(__file__).parent / "Ejercitos/Ty_patrol.json"
            case 'Tyrannofex':
                filepath = Path(__file__).parent / "Ejercitos/Ty_Tyrannofex.json"
            case 'Tyrannofex v2':
                filepath = Path(__file__).parent / "Ejercitos/Ty_Tyrannofex_V2.json"
            case 'Space Marines Patrol':
                filepath = Path(__file__).parent / "Ejercitos/SM_patrol.json"
            case 'Ultramarines Lancer':
                filepath = Path(__file__).parent / "Ejercitos/UM_Lancer.json"
            case 'Ultramarines Lancer v2':
                filepath = Path(__file__).parent / "Ejercitos/UM_Lancer_V2.json"
            case 'Ultramarines 1st & 9th':
                filepath = Path(__file__).parent / "Ejercitos/UM_1st&9th.json"
            case 'Debug':
                filepath = Path(__file__).parent / "Ejercitos/Debug_army.json"
        with open(filepath, 'r', encoding='utf-8') as file:
            dic = json.load(file)
            whlib.Ejercitos_objetos.update({request.player_id-1: whlib.Ejercito(dic, request.player_id)})
        data = {"message": f"Successfully created {whlib.Ejercitos_objetos[request.player_id-1].faccion} army for player {request.player_id}", "army": whlib.Ejercitos_objetos[request.player_id-1].faccion,"player_id": request.player_id}
        return data
            
@app.websocket("/ws")
async def websocket_connection(ws: WebSocket):
    await ws.accept()
    print("Nueva conexión WebSocket establecida")
    conexiones.update({f"{len(conexiones.items())}": ws})
    try:
        print("Iniciando bucle de recepción de datos WebSocket")
        while True:
            datos = await ws.receive()
            respuesta = procesar_request(datos)
    except Exception as e:
        print(f"Error en la conexión WebSocket: {e}")
        for con in conexiones.keys():
            if conexiones[con] == ws:
                conexiones.pop(con)
                break
        for con in conexiones.values():
            try:
                await con.send_json(
                    {"message": "Un jugador se ha desconectado"}
                    )
            except:
                for con in conexiones.keys():
                    if conexiones[con] == ws:
                        conexiones.pop(con)
                        break
            
def procesar_request(datos: dict):
    print(datos)
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
        case _:
            return {"message": "Tipo de request no reconocido", "privado": True}
        
if __name__ == "__main__":
    uvicorn.run(app, host="::1", port=8000)