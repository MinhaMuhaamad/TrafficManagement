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

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Socket.IO with updated config
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000"],
    logger=True,
    engineio_logger=True,
    ping_timeout=120
)
socket_app = socketio.ASGIApp(sio)
app.mount("/ws", socket_app)

# Global state
simulation: Optional[Simulation] = None
city_graphs: Dict[str, CityGraph] = {}
connected_clients = set()

# Models
class SimulationRequest(BaseModel):
    city: str = "San Francisco"

class IncidentRequest(BaseModel):
    lat: float
    lon: float
    type: str

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    connected_clients.add(sid)
    
    # Send initial data if simulation is running
    if simulation and simulation.is_running:
        await send_simulation_data(sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    connected_clients.remove(sid)

async def send_simulation_data(sid=None):
    """Send simulation data to connected clients"""
    if not simulation:
        return
    
    # Get data from simulation
    city_graph = simulation.city_graph.to_dict()
    traffic_lights = simulation.traffic_light_controller.get_traffic_lights()
    vehicles = simulation.vehicle_router.get_vehicles()
    incidents = simulation.get_incidents()
    congestion = simulation.get_congestion_levels()
    
    # Send data to specific client or broadcast to all
    if sid:
        await sio.emit("city_graph", city_graph, to=sid)
        await sio.emit("traffic_lights", traffic_lights, to=sid)
        await sio.emit("vehicles", vehicles, to=sid)
        await sio.emit("incidents", incidents, to=sid)
        await sio.emit("congestion", congestion, to=sid)
    else:
        await sio.emit("city_graph", city_graph)
        await sio.emit("traffic_lights", traffic_lights)
        await sio.emit("vehicles", vehicles)
        await sio.emit("incidents", incidents)
        await sio.emit("congestion", congestion)

# Background task for simulation updates
async def simulation_task():
    while True:
        if simulation and simulation.is_running and connected_clients:
            simulation.update()
            await send_simulation_data()
        await asyncio.sleep(1)  # Update every second

# API routes
@app.get("/")
async def root():
    return {"message": "Smart Traffic Management System API"}

@app.post("/simulation/start")
async def start_simulation(request: SimulationRequest):
    global simulation
    
    try:
        # Create or get city graph
        if request.city not in city_graphs:
            city_graphs[request.city] = CityGraph(request.city)
        
        city_graph = city_graphs[request.city]
        
        # Create simulation components
        traffic_light_controller = TrafficLightController(city_graph)
        vehicle_router = VehicleRouter(city_graph)
        
        # Create and start simulation
        simulation = Simulation(
            city_graph=city_graph,
            traffic_light_controller=traffic_light_controller,
            vehicle_router=vehicle_router
        )
        simulation.start()
        
        return {"status": "success", "message": f"Simulation started for {request.city}"}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.post("/simulation/stop")
async def stop_simulation():
    global simulation
    
    if not simulation:
        return {"status": "error", "message": "No simulation is running"}
    
    simulation.stop()
    return {"status": "success", "message": "Simulation stopped"}

@app.post("/incidents/add")
async def add_incident(request: IncidentRequest):
    if not simulation or not simulation.is_running:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "No simulation is running"}
        )
    
    try:
        incident_id = simulation.add_incident(
            lat=request.lat,
            lon=request.lon,
            incident_type=request.type
        )
        
        return {
            "status": "success", 
            "message": f"{request.type} incident added",
            "incident_id": incident_id
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_task())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
