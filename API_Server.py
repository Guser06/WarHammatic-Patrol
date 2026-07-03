from fastapi import FastAPI, Websocket
from pydantic import BaseModel
import WHmmatic_lib as whlib 
import pathlib as Path
import json

conexiones = {}

app = FastAPI()

class CreateArmyRequest(BaseModel):
    player_id: int
    army_name: str

@app.get("/status")
async def get_status():
    return {"status": "API is running"}

@app.post("/create_army")
async def create_army(request: CreateArmyRequest):
    if request.army_name in whlib.DISPONIBLE:
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
            case '1st & 9th':
                filepath = Path(__file__).parent / "Ejercitos/UM_1st&9th.json"
            case 'Debug':
                filepath = Path(__file__).parent / "Ejercitos/Debug_army.json"
        with open(filepath, 'r') as file:
            dic = json.load(file)
            whlib.Ejercitos_objetos.update({request.player_id-1: whlib.Ejercito(dic, request.player_id)})
            return {"messsage": f"Successfully created {whlib.Ejercitos_objetos[request.player_id-1].faccion} army for player {request.player_id}",
                    "army": whlib.Ejercitos_objetos[request.player_id-1].faccion,
                    "player_id": request.player_id}
            
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