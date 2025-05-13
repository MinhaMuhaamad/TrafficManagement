from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import socketio
import random
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Import our modules
from city_graph import CityGraph
from traffic_light_controller import TrafficLightController
from vehicle_router import VehicleRouter
from simulation import Simulation

app = FastAPI(title="Smart Traffic Management System")

# Configure Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["*"],  # Allow all origins in development
    ping_timeout=60,
    ping_interval=25,
    logger=True,  # Enable logging
    engineio_logger=True  # Enable Engine.IO logging
)

# Create ASGI app
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='socket.io'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the Socket.IO app
app.mount("/", socket_app)

# Initialize simulation components
city_graph = CityGraph()
traffic_controller = TrafficLightController(city_graph)
vehicle_router = VehicleRouter(city_graph)
simulation = Simulation(city_graph, traffic_controller, vehicle_router)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected with headers: {environ.get('HTTP_ORIGIN')}")
    await sio.emit('message', {'data': 'Connected to server'}, to=sid)
    # Send initial data
    await sio.emit('city_graph', city_graph.get_graph_data())
    await sio.emit('traffic_lights', traffic_controller.get_traffic_lights())
    await sio.emit('vehicles', vehicle_router.get_vehicles())
    await sio.emit('simulation_status', {'running': simulation.is_running(), 'message': 'Initial state'})

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def connect_error(sid, error):
    print(f"Connection error for {sid}: {error}")

# Pydantic models
class SimulationStart(BaseModel):
    city: str
    speed: float = 1.0
    routing_algorithm: str = "a_star"
    traffic_light_mode: str = "auto"

class TrafficLightControl(BaseModel):
    node_id: str
    state: str

class VehicleAdd(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    type: str = "car"

class IncidentAdd(BaseModel):
    lat: float
    lon: float
    type: str

class SimulationSettings(BaseModel):
    speed: Optional[float] = None
    routing_algorithm: Optional[str] = None
    traffic_light_mode: Optional[str] = None

# FastAPI routes
@app.post("/simulation/start")
async def start_simulation(settings: SimulationStart):
    try:
        simulation.start(
            city=settings.city,
            speed=settings.speed,
            routing_algorithm=settings.routing_algorithm,
            traffic_light_mode=settings.traffic_light_mode
        )
        return JSONResponse({
            "status": "success",
            "message": f"Simulation started for {settings.city}"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/simulation/stop")
async def stop_simulation():
    try:
        simulation.stop()
        return JSONResponse({
            "status": "success",
            "message": "Simulation stopped"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/simulation/settings")
async def update_simulation_settings(settings: SimulationSettings):
    try:
        simulation.update_settings(
            speed=settings.speed,
            routing_algorithm=settings.routing_algorithm,
            traffic_light_mode=settings.traffic_light_mode
        )
        return JSONResponse({
            "status": "success",
            "message": "Simulation settings updated"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/traffic_lights/control")
async def control_traffic_light(control: TrafficLightControl):
    try:
        success = traffic_controller.set_traffic_light(control.node_id, control.state)
        if success:
            await sio.emit('traffic_lights', traffic_controller.get_traffic_lights())
            return JSONResponse({
                "status": "success",
                "message": f"Traffic light {control.node_id} set to {control.state}"
            })
        else:
            return JSONResponse({
                "status": "error",
                "message": "Failed to control traffic light"
            }, status_code=400)
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/vehicles/add")
async def add_vehicle(vehicle: VehicleAdd):
    try:
        vehicle_id = vehicle_router.add_vehicle(
            vehicle.origin,
            vehicle.destination,
            vehicle.type
        )
        await sio.emit('vehicles', vehicle_router.get_vehicles())
        return JSONResponse({
            "status": "success",
            "message": f"Vehicle {vehicle_id} added",
            "vehicle_id": vehicle_id
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/incidents/add")
async def add_incident(incident: IncidentAdd):
    try:
        simulation.add_incident(incident.lat, incident.lon, incident.type)
        await sio.emit('incidents', simulation.get_incidents())
        return JSONResponse({
            "status": "success",
            "message": f"{incident.type} incident added"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/analytics")
async def get_analytics():
    try:
        return JSONResponse(simulation.get_analytics())
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

# Simulation loop
async def simulation_loop():
    while True:
        if simulation.is_running():
            simulation.update()
            await sio.emit('city_graph', city_graph.get_graph_data())
            await sio.emit('traffic_lights', traffic_controller.get_traffic_lights())
            await sio.emit('vehicles', vehicle_router.get_vehicles())
            await sio.emit('incidents', simulation.get_incidents())
            await sio.emit('congestion', simulation.get_congestion_levels())
            await sio.emit('analytics', simulation.get_analytics())
            await sio.emit('simulation_status', {
                'running': simulation.is_running(),
                'message': 'Simulation update'
            })
        await asyncio.sleep(0.1)  # Update every 100ms

# Start simulation loop on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",  # Enable debug logging
        reload=True
    )