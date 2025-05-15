from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import socketio
import random
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Create FastAPI app
app = FastAPI(title="Simple WebSocket Server")

# Add CORS middleware FIRST - order matters!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Expose all headers
)

# Configure Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["*"],  # Allow all origins in development
    ping_timeout=120,  # Increase timeout
    ping_interval=25,
    logger=True,  # Enable logging
    engineio_logger=True,  # Enable Engine.IO logging
    always_connect=True  # Always accept connections
)

# Create ASGI app
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='socket.io'
)

# Mount the Socket.IO app
app.mount("/", socket_app)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected with headers: {environ.get('HTTP_ORIGIN')}")
    await sio.emit('message', {'data': 'Connected to server'}, to=sid)
    # Send some dummy data
    await sio.emit('city_graph', {'nodes': [], 'edges': []}, to=sid)
    await sio.emit('traffic_lights', [], to=sid)
    await sio.emit('vehicles', [], to=sid)
    await sio.emit('simulation_status', {'running': False, 'message': 'Initial state'}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def connect_error(sid, error):
    print(f"Connection error for {sid}: {error}")

# Simple API endpoint
@app.get("/api/status")
async def get_status():
    return JSONResponse({
        "status": "success",
        "message": "Server is running",
        "timestamp": datetime.now().isoformat()
    })

# Simulation loop to send periodic updates
async def simulation_loop():
    while True:
        # Send dummy updates every second
        await sio.emit('message', {'data': f'Server time: {datetime.now().isoformat()}'})
        await asyncio.sleep(1)

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
        reload=False
    )
