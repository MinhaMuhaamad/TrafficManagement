from fastapi import FastAPI, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional

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

# City data definitions
CITY_DATA = {
    "San Francisco": {
        "center": [37.7749, -122.4194],
        "zoom": 13,
        "nodes": [
            {"id": "sf1", "lat": 37.7749, "lon": -122.4194, "name": "Downtown SF"},
            {"id": "sf2", "lat": 37.7749, "lon": -122.4294, "name": "Golden Gate Park"},
            {"id": "sf3", "lat": 37.7849, "lon": -122.4194, "name": "Fisherman's Wharf"},
            {"id": "sf4", "lat": 37.7829, "lon": -122.4324, "name": "Presidio"},
            {"id": "sf5", "lat": 37.7699, "lon": -122.4134, "name": "Mission District"}
        ],
        "edges": [
            {"id": "sf_e1", "source_id": "sf1", "target_id": "sf2", "source_lat": 37.7749, "source_lon": -122.4194, "target_lat": 37.7749, "target_lon": -122.4294, "name": "Market Street"},
            {"id": "sf_e2", "source_id": "sf2", "target_id": "sf3", "source_lat": 37.7749, "source_lon": -122.4294, "target_lat": 37.7849, "target_lon": -122.4194, "name": "Van Ness Ave"},
            {"id": "sf_e3", "source_id": "sf3", "target_id": "sf4", "source_lat": 37.7849, "source_lon": -122.4194, "target_lat": 37.7829, "target_lon": -122.4324, "name": "Lombard Street"},
            {"id": "sf_e4", "source_id": "sf4", "target_id": "sf5", "source_lat": 37.7829, "source_lon": -122.4324, "target_lat": 37.7699, "target_lon": -122.4134, "name": "Divisadero St"},
            {"id": "sf_e5", "source_id": "sf5", "target_id": "sf1", "source_lat": 37.7699, "source_lon": -122.4134, "target_lat": 37.7749, "target_lon": -122.4194, "name": "Mission Street"}
        ],
        "traffic_lights": [
            {"id": "sf_tl1", "lat": 37.7749, "lon": -122.4194, "state": "green", "next_change": 30, "queue_length": 0},
            {"id": "sf_tl2", "lat": 37.7749, "lon": -122.4294, "state": "red", "next_change": 15, "queue_length": 3},
            {"id": "sf_tl3", "lat": 37.7849, "lon": -122.4194, "state": "yellow", "next_change": 5, "queue_length": 2},
            {"id": "sf_tl4", "lat": 37.7829, "lon": -122.4324, "state": "green", "next_change": 25, "queue_length": 1},
            {"id": "sf_tl5", "lat": 37.7699, "lon": -122.4134, "state": "red", "next_change": 20, "queue_length": 4}
        ],
        "vehicle_count": 15  # Number of vehicles to generate for this city
    },
    "New York": {
        "center": [40.7128, -74.0060],
        "zoom": 13,
        "nodes": [
            {"id": "ny1", "lat": 40.7128, "lon": -74.0060, "name": "Downtown Manhattan"},
            {"id": "ny2", "lat": 40.7328, "lon": -73.9860, "name": "Midtown"},
            {"id": "ny3", "lat": 40.7528, "lon": -73.9660, "name": "Upper East Side"},
            {"id": "ny4", "lat": 40.7428, "lon": -73.9960, "name": "Times Square"},
            {"id": "ny5", "lat": 40.7028, "lon": -74.0160, "name": "Financial District"}
        ],
        "edges": [
            {"id": "ny_e1", "source_id": "ny1", "target_id": "ny2", "source_lat": 40.7128, "source_lon": -74.0060, "target_lat": 40.7328, "target_lon": -73.9860, "name": "Broadway"},
            {"id": "ny_e2", "source_id": "ny2", "target_id": "ny3", "source_lat": 40.7328, "source_lon": -73.9860, "target_lat": 40.7528, "target_lon": -73.9660, "name": "5th Avenue"},
            {"id": "ny_e3", "source_id": "ny3", "target_id": "ny4", "source_lat": 40.7528, "source_lon": -73.9660, "target_lat": 40.7428, "target_lon": -73.9960, "name": "Park Avenue"},
            {"id": "ny_e4", "source_id": "ny4", "target_id": "ny5", "source_lat": 40.7428, "source_lon": -73.9960, "target_lat": 40.7028, "target_lon": -74.0160, "name": "7th Avenue"},
            {"id": "ny_e5", "source_id": "ny5", "target_id": "ny1", "source_lat": 40.7028, "source_lon": -74.0160, "target_lat": 40.7128, "target_lon": -74.0060, "name": "Wall Street"}
        ],
        "traffic_lights": [
            {"id": "ny_tl1", "lat": 40.7128, "lon": -74.0060, "state": "green", "next_change": 30, "queue_length": 0},
            {"id": "ny_tl2", "lat": 40.7328, "lon": -73.9860, "state": "red", "next_change": 15, "queue_length": 5},
            {"id": "ny_tl3", "lat": 40.7528, "lon": -73.9660, "state": "yellow", "next_change": 5, "queue_length": 3},
            {"id": "ny_tl4", "lat": 40.7428, "lon": -73.9960, "state": "green", "next_change": 25, "queue_length": 7},
            {"id": "ny_tl5", "lat": 40.7028, "lon": -74.0160, "state": "red", "next_change": 20, "queue_length": 4}
        ],
        "vehicle_count": 25  # More vehicles for New York
    },
    "Chicago": {
        "center": [41.8781, -87.6298],
        "zoom": 13,
        "nodes": [
            {"id": "chi1", "lat": 41.8781, "lon": -87.6298, "name": "The Loop"},
            {"id": "chi2", "lat": 41.8981, "lon": -87.6198, "name": "River North"},
            {"id": "chi3", "lat": 41.8881, "lon": -87.6398, "name": "West Loop"},
            {"id": "chi4", "lat": 41.8681, "lon": -87.6198, "name": "South Loop"},
            {"id": "chi5", "lat": 41.8881, "lon": -87.6098, "name": "Magnificent Mile"}
        ],
        "edges": [
            {"id": "chi_e1", "source_id": "chi1", "target_id": "chi2", "source_lat": 41.8781, "source_lon": -87.6298, "target_lat": 41.8981, "target_lon": -87.6198, "name": "Michigan Ave"},
            {"id": "chi_e2", "source_id": "chi2", "target_id": "chi3", "source_lat": 41.8981, "source_lon": -87.6198, "target_lat": 41.8881, "target_lon": -87.6398, "name": "Chicago Ave"},
            {"id": "chi_e3", "source_id": "chi3", "target_id": "chi4", "source_lat": 41.8881, "source_lon": -87.6398, "target_lat": 41.8681, "target_lon": -87.6198, "name": "Randolph St"},
            {"id": "chi_e4", "source_id": "chi4", "target_id": "chi5", "source_lat": 41.8681, "source_lon": -87.6198, "target_lat": 41.8881, "target_lon": -87.6098, "name": "State St"},
            {"id": "chi_e5", "source_id": "chi5", "target_id": "chi1", "source_lat": 41.8881, "source_lon": -87.6098, "target_lat": 41.8781, "target_lon": -87.6298, "name": "Wacker Dr"}
        ],
        "traffic_lights": [
            {"id": "chi_tl1", "lat": 41.8781, "lon": -87.6298, "state": "green", "next_change": 30, "queue_length": 2},
            {"id": "chi_tl2", "lat": 41.8981, "lon": -87.6198, "state": "red", "next_change": 15, "queue_length": 4},
            {"id": "chi_tl3", "lat": 41.8881, "lon": -87.6398, "state": "yellow", "next_change": 5, "queue_length": 1},
            {"id": "chi_tl4", "lat": 41.8681, "lon": -87.6198, "state": "green", "next_change": 25, "queue_length": 3},
            {"id": "chi_tl5", "lat": 41.8881, "lon": -87.6098, "state": "red", "next_change": 20, "queue_length": 5}
        ],
        "vehicle_count": 20
    },
    "Boston": {
        "center": [42.3601, -71.0589],
        "zoom": 13,
        "nodes": [
            {"id": "bos1", "lat": 42.3601, "lon": -71.0589, "name": "Downtown Boston"},
            {"id": "bos2", "lat": 42.3501, "lon": -71.0689, "name": "Back Bay"},
            {"id": "bos3", "lat": 42.3701, "lon": -71.0489, "name": "North End"},
            {"id": "bos4", "lat": 42.3401, "lon": -71.0489, "name": "Seaport"},
            {"id": "bos5", "lat": 42.3601, "lon": -71.0789, "name": "Fenway"}
        ],
        "edges": [
            {"id": "bos_e1", "source_id": "bos1", "target_id": "bos2", "source_lat": 42.3601, "source_lon": -71.0589, "target_lat": 42.3501, "target_lon": -71.0689, "name": "Boylston St"},
            {"id": "bos_e2", "source_id": "bos2", "target_id": "bos3", "source_lat": 42.3501, "source_lon": -71.0689, "target_lat": 42.3701, "target_lon": -71.0489, "name": "Commonwealth Ave"},
            {"id": "bos_e3", "source_id": "bos3", "target_id": "bos4", "source_lat": 42.3701, "source_lon": -71.0489, "target_lat": 42.3401, "target_lon": -71.0489, "name": "Atlantic Ave"},
            {"id": "bos_e4", "source_id": "bos4", "target_id": "bos5", "source_lat": 42.3401, "source_lon": -71.0489, "target_lat": 42.3601, "target_lon": -71.0789, "name": "Tremont St"},
            {"id": "bos_e5", "source_id": "bos5", "target_id": "bos1", "source_lat": 42.3601, "source_lon": -71.0789, "target_lat": 42.3601, "target_lon": -71.0589, "name": "Beacon St"}
        ],
        "traffic_lights": [
            {"id": "bos_tl1", "lat": 42.3601, "lon": -71.0589, "state": "green", "next_change": 30, "queue_length": 1},
            {"id": "bos_tl2", "lat": 42.3501, "lon": -71.0689, "state": "red", "next_change": 15, "queue_length": 3},
            {"id": "bos_tl3", "lat": 42.3701, "lon": -71.0489, "state": "yellow", "next_change": 5, "queue_length": 2},
            {"id": "bos_tl4", "lat": 42.3401, "lon": -71.0489, "state": "green", "next_change": 25, "queue_length": 0},
            {"id": "bos_tl5", "lat": 42.3601, "lon": -71.0789, "state": "red", "next_change": 20, "queue_length": 4}
        ],
        "vehicle_count": 18
    },
    "Seattle": {
        "center": [47.6062, -122.3321],
        "zoom": 13,
        "nodes": [
            {"id": "sea1", "lat": 47.6062, "lon": -122.3321, "name": "Downtown Seattle"},
            {"id": "sea2", "lat": 47.6162, "lon": -122.3421, "name": "Space Needle"},
            {"id": "sea3", "lat": 47.6262, "lon": -122.3221, "name": "Capitol Hill"},
            {"id": "sea4", "lat": 47.5962, "lon": -122.3221, "name": "Pioneer Square"},
            {"id": "sea5", "lat": 47.6162, "lon": -122.3121, "name": "First Hill"}
        ],
        "edges": [
            {"id": "sea_e1", "source_id": "sea1", "target_id": "sea2", "source_lat": 47.6062, "source_lon": -122.3321, "target_lat": 47.6162, "target_lon": -122.3421, "name": "5th Ave"},
            {"id": "sea_e2", "source_id": "sea2", "target_id": "sea3", "source_lat": 47.6162, "source_lon": -122.3421, "target_lat": 47.6262, "target_lon": -122.3221, "name": "Denny Way"},
            {"id": "sea_e3", "source_id": "sea3", "target_id": "sea4", "source_lat": 47.6262, "source_lon": -122.3221, "target_lat": 47.5962, "target_lon": -122.3221, "name": "Broadway"},
            {"id": "sea_e4", "source_id": "sea4", "target_id": "sea5", "source_lat": 47.5962, "source_lon": -122.3221, "target_lat": 47.6162, "target_lon": -122.3121, "name": "James St"},
            {"id": "sea_e5", "source_id": "sea5", "target_id": "sea1", "source_lat": 47.6162, "source_lon": -122.3121, "target_lat": 47.6062, "target_lon": -122.3321, "name": "Madison St"}
        ],
        "traffic_lights": [
            {"id": "sea_tl1", "lat": 47.6062, "lon": -122.3321, "state": "green", "next_change": 30, "queue_length": 2},
            {"id": "sea_tl2", "lat": 47.6162, "lon": -122.3421, "state": "red", "next_change": 15, "queue_length": 4},
            {"id": "sea_tl3", "lat": 47.6262, "lon": -122.3221, "state": "yellow", "next_change": 5, "queue_length": 1},
            {"id": "sea_tl4", "lat": 47.5962, "lon": -122.3221, "state": "green", "next_change": 25, "queue_length": 3},
            {"id": "sea_tl5", "lat": 47.6162, "lon": -122.3121, "state": "red", "next_change": 20, "queue_length": 2}
        ],
        "vehicle_count": 16
    }
}

# Global variables to track simulation state
simulation_running = False
connected_clients = []
current_city = "San Francisco"  # Default city

# Helper function to generate vehicles for a city
def generate_vehicles_for_city(city_name):
    city_data = CITY_DATA[city_name]
    nodes = city_data["nodes"]
    vehicle_count = city_data["vehicle_count"]
    vehicles = []

    # Vehicle types with their probabilities
    vehicle_types = ["car", "car", "car", "bus", "truck"]  # 60% cars, 20% buses, 20% trucks

    for i in range(vehicle_count):
        # Randomly select origin and destination nodes
        origin_node = random.choice(nodes)
        destination_node = random.choice([n for n in nodes if n["id"] != origin_node["id"]])

        # Randomly select vehicle type
        vehicle_type = random.choice(vehicle_types)

        # Generate random speed based on vehicle type
        base_speed = 25 if vehicle_type == "car" else (20 if vehicle_type == "bus" else 15)
        speed = base_speed + random.uniform(-5, 10)

        # Calculate ETA (just a rough estimate)
        eta = datetime.now().timestamp() + random.randint(60, 300)  # 1-5 minutes

        # Generate a position somewhere between origin and destination
        progress = random.uniform(0.1, 0.9)  # How far along the route
        lat = origin_node["lat"] + (destination_node["lat"] - origin_node["lat"]) * progress
        lon = origin_node["lon"] + (destination_node["lon"] - origin_node["lon"]) * progress

        # Create a simple route
        route = [
            {"lat": origin_node["lat"], "lon": origin_node["lon"]},
            {"lat": lat, "lon": lon},
            {"lat": destination_node["lat"], "lon": destination_node["lon"]}
        ]

        # Add some randomness to the route
        for point in route[1:-1]:  # Don't modify start and end points
            point["lat"] += random.uniform(-0.001, 0.001)
            point["lon"] += random.uniform(-0.001, 0.001)

        vehicles.append({
            "id": f"{city_name.lower().replace(' ', '_')}_{i+1}",
            "type": vehicle_type,
            "lat": lat,
            "lon": lon,
            "origin": origin_node["name"],
            "destination": destination_node["name"],
            "speed": speed,
            "status": "moving",
            "eta": eta,
            "current_route": route
        })

    return vehicles

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global current_city
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

        # Send city-specific graph data
        city_data = CITY_DATA[current_city]
        await websocket.send_json({
            "type": "city_graph",
            "data": {
                "nodes": city_data["nodes"],
                "edges": city_data["edges"]
            }
        })

        # Send city-specific traffic lights data
        await websocket.send_json({
            "type": "traffic_lights",
            "data": city_data["traffic_lights"]
        })

        # Generate and send city-specific vehicles data
        vehicles = generate_vehicles_for_city(current_city)
        await websocket.send_json({
            "type": "vehicles",
            "data": vehicles
        })

        # Use asyncio for sleep

        # Main WebSocket loop
        while True:
            # If simulation is running, send periodic updates
            if simulation_running:
                # Get current timestamp for ETA calculation
                current_time = datetime.now().timestamp()

                # Get current city data
                city_data = CITY_DATA[current_city]

                # Generate updated vehicles with dynamic movement
                vehicles = generate_vehicles_for_city(current_city)

                # Add some random movement to each vehicle
                for vehicle in vehicles:
                    vehicle["lat"] += random.uniform(-0.0005, 0.0005)
                    vehicle["lon"] += random.uniform(-0.0005, 0.0005)
                    vehicle["speed"] += random.uniform(-2, 2)

                    # Ensure speed doesn't go below 5
                    vehicle["speed"] = max(5, vehicle["speed"])

                # Send updated vehicles
                await websocket.send_json({
                    "type": "vehicles",
                    "data": vehicles
                })

                # Send updated traffic light states with dynamic changes
                light_states = ["red", "green", "yellow"]
                current_second = datetime.now().second

                # Update traffic light states
                updated_traffic_lights = []
                for i, light in enumerate(city_data["traffic_lights"]):
                    updated_light = light.copy()
                    updated_light["state"] = light_states[(current_second // 10 + i) % 3]
                    updated_light["next_change"] = current_time + (10 - current_second % 10)
                    updated_light["queue_length"] = random.randint(0, 5)
                    updated_traffic_lights.append(updated_light)

                await websocket.send_json({
                    "type": "traffic_lights",
                    "data": updated_traffic_lights
                })

            # Wait for a shorter time to make the simulation run faster
            await asyncio.sleep(0.3)  # Update 3 times per second for smoother animation
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

# City endpoints
@app.post("/city/change")
async def change_city(city_data: dict):
    global current_city

    city_name = city_data.get("city")
    if not city_name or city_name not in CITY_DATA:
        return {
            "status": "error",
            "message": f"Invalid city name. Available cities: {', '.join(CITY_DATA.keys())}",
            "timestamp": datetime.now().isoformat()
        }

    # Update current city
    current_city = city_name

    # Get city data
    city_info = CITY_DATA[current_city]

    # Generate new vehicles for this city
    vehicles = generate_vehicles_for_city(current_city)

    # Notify all clients about the city change
    await broadcast_message("city_graph", {
        "nodes": city_info["nodes"],
        "edges": city_info["edges"]
    })

    await broadcast_message("traffic_lights", city_info["traffic_lights"])

    await broadcast_message("vehicles", vehicles)

    # Also send map center update
    await broadcast_message("map_center", {
        "center": city_info["center"],
        "zoom": city_info["zoom"]
    })

    return {
        "status": "success",
        "message": f"City changed to {current_city}",
        "timestamp": datetime.now().isoformat(),
        "city": current_city
    }

# Simulation endpoints
@app.post("/simulation/start")
async def start_simulation(simulation_data: dict = None):
    global simulation_running, current_city
    simulation_running = True

    # If city is provided in the request, update current city
    if simulation_data and "city" in simulation_data:
        city_name = simulation_data["city"]
        if city_name in CITY_DATA:
            current_city = city_name

            # Send updated city data
            city_info = CITY_DATA[current_city]
            await broadcast_message("city_graph", {
                "nodes": city_info["nodes"],
                "edges": city_info["edges"]
            })

            await broadcast_message("traffic_lights", city_info["traffic_lights"])

            # Generate new vehicles for this city
            vehicles = generate_vehicles_for_city(current_city)
            await broadcast_message("vehicles", vehicles)

            # Also send map center update
            await broadcast_message("map_center", {
                "center": city_info["center"],
                "zoom": city_info["zoom"]
            })

    # Notify all clients that simulation has started
    await broadcast_message("simulation_status", {
        "running": True,
        "message": f"Simulation started for {current_city}",
        "status": "success"
    })

    return {
        "status": "success",
        "message": f"Simulation started for {current_city}",
        "timestamp": datetime.now().isoformat(),
        "running": True,
        "city": current_city
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
        "running": False,
        "city": current_city
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Use a different port
        log_level="info"
    )
