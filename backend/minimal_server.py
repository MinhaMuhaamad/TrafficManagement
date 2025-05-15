from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from datetime import datetime

# Create FastAPI app
app = FastAPI(title="Minimal WebSocket Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global variables to track simulation state
simulation_running = False
connected_clients = []

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        # Send initial data
        await websocket.send_json({
            "type": "simulation_status",
            "data": {
                "running": simulation_running,
                "message": "Connected to server",
                "status": "info"
            }
        })

        # Send dummy city graph data
        await websocket.send_json({
            "type": "city_graph",
            "data": {
                "nodes": [
                    {"id": "1", "lat": 37.7749, "lon": -122.4194, "name": "Node 1"},
                    {"id": "2", "lat": 37.7749, "lon": -122.4294, "name": "Node 2"},
                    {"id": "3", "lat": 37.7849, "lon": -122.4194, "name": "Node 3"}
                ],
                "edges": [
                    {"id": "1", "source_id": "1", "target_id": "2", "source_lat": 37.7749, "source_lon": -122.4194, "target_lat": 37.7749, "target_lon": -122.4294, "name": "Edge 1"},
                    {"id": "2", "source_id": "2", "target_id": "3", "source_lat": 37.7749, "source_lon": -122.4294, "target_lat": 37.7849, "target_lon": -122.4194, "name": "Edge 2"}
                ]
            }
        })

        # Send dummy traffic lights data
        await websocket.send_json({
            "type": "traffic_lights",
            "data": [
                {"id": "1", "lat": 37.7749, "lon": -122.4194, "state": "green", "next_change": 30, "queue_length": 0},
                {"id": "2", "lat": 37.7749, "lon": -122.4294, "state": "red", "next_change": 15, "queue_length": 3}
            ]
        })

        # Send dummy vehicles data
        await websocket.send_json({
            "type": "vehicles",
            "data": [
                {"id": "1", "type": "car", "lat": 37.7749, "lon": -122.4244, "origin": "Node 1", "destination": "Node 2", "speed": 30, "status": "moving", "eta": 120},
                {"id": "2", "type": "bus", "lat": 37.7799, "lon": -122.4194, "origin": "Node 1", "destination": "Node 3", "speed": 25, "status": "moving", "eta": 180}
            ]
        })

        # Use asyncio for sleep

        # Main WebSocket loop
        while True:
            # If simulation is running, send periodic updates
            if simulation_running:
                # Send updated vehicle positions
                await websocket.send_json({
                    "type": "vehicles",
                    "data": [
                        {"id": "1", "type": "car", "lat": 37.7749 + 0.001, "lon": -122.4244 + 0.001, "origin": "Node 1", "destination": "Node 2", "speed": 30, "status": "moving", "eta": 120},
                        {"id": "2", "type": "bus", "lat": 37.7799 + 0.001, "lon": -122.4194 + 0.001, "origin": "Node 1", "destination": "Node 3", "speed": 25, "status": "moving", "eta": 180}
                    ]
                })

                # Send updated traffic light states
                await websocket.send_json({
                    "type": "traffic_lights",
                    "data": [
                        {"id": "1", "lat": 37.7749, "lon": -122.4194, "state": "yellow", "next_change": 5, "queue_length": 2},
                        {"id": "2", "lat": 37.7749, "lon": -122.4294, "state": "green", "next_change": 25, "queue_length": 0}
                    ]
                })

            # Wait for 1 second before sending the next update
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

# Simple API endpoint - supports both GET and POST
@app.get("/api/status")
async def get_status():
    return {
        "status": "success",
        "message": "Server is running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/status")
async def post_status():
    return {
        "status": "success",
        "message": "Simulation status updated",
        "timestamp": datetime.now().isoformat(),
        "running": True
    }

# Helper function to broadcast to all clients
async def broadcast_message(message_type, data):
    for client in connected_clients:
        try:
            await client.send_json({
                "type": message_type,
                "data": data
            })
        except Exception as e:
            print(f"Error broadcasting to client: {e}")

# Simulation endpoints
@app.post("/simulation/start")
async def start_simulation():
    global simulation_running
    simulation_running = True

    # Notify all clients that simulation has started
    await broadcast_message("simulation_status", {
        "running": True,
        "message": "Simulation started",
        "status": "success"
    })

    return {
        "status": "success",
        "message": "Simulation started",
        "timestamp": datetime.now().isoformat(),
        "running": True
    }

@app.post("/simulation/stop")
async def stop_simulation():
    global simulation_running
    simulation_running = False

    # Notify all clients that simulation has stopped
    await broadcast_message("simulation_status", {
        "running": False,
        "message": "Simulation stopped",
        "status": "info"
    })

    return {
        "status": "success",
        "message": "Simulation stopped",
        "timestamp": datetime.now().isoformat(),
        "running": False
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Use a different port
        log_level="info"
    )
