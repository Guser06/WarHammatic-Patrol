from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

conexiones = []

app = FastAPI()

# 1. Define your standard Python class and its methods
class Car:
    def __init__(self, brand: str, model: str):
        self.brand = brand
        self.model = model
        self.is_running = False

    def start_engine(self) -> str:
        self.is_running = True
        return f"The engine of the {self.brand} {self.model} has started successfully!"


# 2. Define the Pydantic schema to validate incoming POST request data
class CarCreateRequest(BaseModel):
    brand: str
    model: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conexiones.append(websocket)
    try:
        while True:
            datos = await websocket.receive_json()
            respuesta = procesar_request(datos)
            for conexion in conexiones:
                await conexion.send(respuesta)
    except Exception:
        conexiones.remove(websocket)

def procesar_request(datos: dict):
    if datos["message"] is not None:
        return {"status": "received",
                "message": datos["message"]
                }
    
    return {"respuesta": "wawa"}

# 3. Create the POST route, instantiate the class, and call the method
@app.post("/cars/start")
def create_car_and_start(payload: CarCreateRequest):
    # Instantiate the class using validated data from the request body
    my_car = Car(brand=payload.brand, model=payload.model)
    
    # Trigger the class method
    result_message = my_car.start_engine()
    
    # Return the response
    return {
        "status": "success",
        "message": result_message,
        "current_state": {"is_running": my_car.is_running}
    }
