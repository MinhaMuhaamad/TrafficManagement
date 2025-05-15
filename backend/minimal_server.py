from fastapi import FastAPI, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import random
import heapq
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

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

# Analytics data storage
analytics_data = {
    "trafficLightEfficiency": 0.0,
    "previousTrafficLightEfficiency": 0.0,
    "averageWaitTime": 0.0,
    "previousAverageWaitTime": 0.0,
    "congestionTrend": [0.0, 0.0, 0.0],
    "speedHistory": [0.0, 0.0, 0.0],
    "affectedVehicles": 0,
    "reroutedVehicles": 0,
    "averageIncidentDelay": 0,
    "trafficLightOptimizationStatus": "Active",
    "routeOptimizationStatus": "Active",
    "congestionManagementStatus": "Active"
}

# Incidents storage
incidents = []

# Smart City Traffic Management Functions

# Function to build a graph from city data
def build_city_graph(city_data, congestion_levels=None):
    """
    Build a graph representation of the city for routing algorithms
    Returns a dictionary where keys are node IDs and values are dictionaries of neighbors with travel times
    """
    graph = {}

    # Initialize all nodes
    for node in city_data["nodes"]:
        graph[node["id"]] = {}

    # Add edges with travel times
    for edge in city_data["edges"]:
        source_id = edge["source_id"]
        target_id = edge["target_id"]

        # Calculate distance using Haversine formula (for realistic travel time)
        source_lat, source_lon = edge["source_lat"], edge["source_lon"]
        target_lat, target_lon = edge["target_lat"], edge["target_lon"]

        # Calculate distance in kilometers
        R = 6371  # Earth radius in kilometers
        dLat = math.radians(target_lat - source_lat)
        dLon = math.radians(target_lon - source_lon)
        a = (math.sin(dLat/2) * math.sin(dLat/2) +
             math.cos(math.radians(source_lat)) * math.cos(math.radians(target_lat)) *
             math.sin(dLon/2) * math.sin(dLon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        # Base travel time (in minutes) - assuming 30 km/h average speed
        base_travel_time = (distance / 30) * 60

        # Apply congestion factor if available
        congestion_factor = 1.0
        if congestion_levels and edge["id"] in congestion_levels:
            # Congestion increases travel time (1.0 = no congestion, 5.0 = severe congestion)
            congestion_factor = 1.0 + (congestion_levels[edge["id"]] * 4.0)

        travel_time = base_travel_time * congestion_factor

        # Add edge in both directions (assuming bidirectional roads)
        graph[source_id][target_id] = travel_time
        graph[target_id][source_id] = travel_time

    return graph

# Dijkstra's algorithm for shortest path
def find_shortest_path(graph, start_node, end_node):
    """
    Find the shortest path between start_node and end_node using Dijkstra's algorithm
    Returns a tuple of (path, travel_time) where path is a list of node IDs
    """
    # Priority queue for Dijkstra's algorithm
    queue = [(0, start_node, [])]  # (travel_time, current_node, path)
    visited = set()

    while queue:
        # Get node with smallest travel time
        travel_time, current, path = heapq.heappop(queue)

        # If we've reached the destination, return the path and travel time
        if current == end_node:
            return path + [current], travel_time

        # Skip if we've already visited this node
        if current in visited:
            continue

        # Mark as visited
        visited.add(current)

        # Add neighbors to queue
        for neighbor, edge_time in graph.get(current, {}).items():
            if neighbor not in visited:
                heapq.heappush(queue, (travel_time + edge_time, neighbor, path + [current]))

    # No path found
    return None, float('inf')

# Function to optimize traffic light timings
def optimize_traffic_lights(city_data, congestion_levels, traffic_lights):
    """
    Optimize traffic light timings based on current congestion levels
    Returns updated traffic light data
    """
    optimized_lights = []

    # Create a mapping of node IDs to traffic lights
    node_to_light = {}
    for light in traffic_lights:
        # Find the closest node to this traffic light
        closest_node = None
        min_distance = float('inf')

        for node in city_data["nodes"]:
            # Calculate distance between light and node
            distance = math.sqrt(
                (light["lat"] - node["lat"])**2 +
                (light["lon"] - node["lon"])**2
            )

            if distance < min_distance:
                min_distance = distance
                closest_node = node["id"]

        if closest_node:
            node_to_light[closest_node] = light

    # For each traffic light, adjust timing based on incoming road congestion
    for light in traffic_lights:
        updated_light = light.copy()

        # Find the node this light is associated with
        closest_node = None
        min_distance = float('inf')

        for node in city_data["nodes"]:
            distance = math.sqrt(
                (light["lat"] - node["lat"])**2 +
                (light["lon"] - node["lon"])**2
            )

            if distance < min_distance:
                min_distance = distance
                closest_node = node["id"]

        if closest_node:
            # Find all edges connected to this node
            incoming_edges = []
            for edge in city_data["edges"]:
                if edge["target_id"] == closest_node or edge["source_id"] == closest_node:
                    incoming_edges.append(edge["id"])

            # Calculate average congestion on incoming edges
            avg_congestion = 0.0
            if incoming_edges:
                total_congestion = sum(congestion_levels.get(edge_id, 0.0) for edge_id in incoming_edges)
                avg_congestion = total_congestion / len(incoming_edges)

            # Adjust green time based on congestion
            # Higher congestion = longer green time (up to a limit)
            base_green_time = 30  # Base green time in seconds
            max_adjustment = 30   # Maximum adjustment in seconds

            # Calculate adjustment factor (0 to 1)
            adjustment_factor = min(1.0, avg_congestion * 1.5)

            # Apply adjustment
            green_time = base_green_time + (adjustment_factor * max_adjustment)

            # Update the light timing
            updated_light["next_change"] = datetime.now().timestamp() + green_time

            # Prioritize green for congested directions
            if avg_congestion > 0.5:  # If congestion is high
                updated_light["state"] = "green"

        optimized_lights.append(updated_light)

    return optimized_lights

# Function to suggest rerouting for vehicles based on current conditions
def suggest_rerouting(vehicles, city_data, congestion_levels, incidents):
    """
    Suggest new routes for vehicles based on current traffic conditions
    Returns updated vehicle data with new routes
    """
    # Build the city graph with current congestion levels
    city_graph = build_city_graph(city_data, congestion_levels)

    # Create a mapping of node names to IDs for easier lookup
    node_name_to_id = {node["name"]: node["id"] for node in city_data["nodes"]}
    node_id_to_node = {node["id"]: node for node in city_data["nodes"]}

    updated_vehicles = []

    for vehicle in vehicles:
        updated_vehicle = vehicle.copy()

        # Skip vehicles that have already arrived
        if vehicle["status"] == "arrived":
            updated_vehicles.append(updated_vehicle)
            continue

        # Find node IDs for origin and destination
        origin_id = None
        destination_id = None

        for node in city_data["nodes"]:
            if node["name"] == vehicle["origin"]:
                origin_id = node["id"]
            if node["name"] == vehicle["destination"]:
                destination_id = node["id"]

        # If we can't find the nodes, skip this vehicle
        if not origin_id or not destination_id:
            updated_vehicles.append(updated_vehicle)
            continue

        # Find the current position's closest node
        current_pos_node = None
        min_distance = float('inf')

        for node in city_data["nodes"]:
            distance = math.sqrt(
                (vehicle["lat"] - node["lat"])**2 +
                (vehicle["lon"] - node["lon"])**2
            )

            if distance < min_distance:
                min_distance = distance
                current_pos_node = node["id"]

        # If we can't determine current position, use origin
        if not current_pos_node:
            current_pos_node = origin_id

        # Find the shortest path from current position to destination
        path, travel_time = find_shortest_path(city_graph, current_pos_node, destination_id)

        # If a path is found, update the vehicle's route
        if path:
            # Convert node IDs to coordinates for the route
            new_route = []
            for node_id in path:
                node = node_id_to_node[node_id]
                new_route.append({"lat": node["lat"], "lon": node["lon"]})

            # Update the vehicle's route and ETA
            updated_vehicle["current_route"] = new_route
            updated_vehicle["eta"] = datetime.now().timestamp() + (travel_time * 60)  # Convert minutes to seconds

            # Check if the vehicle is affected by incidents
            for incident in incidents:
                # Calculate distance to incident
                incident_distance = math.sqrt(
                    (vehicle["lat"] - incident["lat"])**2 +
                    (vehicle["lon"] - incident["lon"])**2
                )

                # If vehicle is close to an incident, mark it as affected
                if incident_distance < 0.01:  # Approximately 1km
                    updated_vehicle["status"] = "rerouting"
                    # Add some delay due to the incident
                    updated_vehicle["eta"] += random.randint(300, 900)  # 5-15 minutes delay

        updated_vehicles.append(updated_vehicle)

    return updated_vehicles

# Helper function to calculate analytics data
def calculate_analytics_data(vehicles, traffic_lights, city_data):
    global analytics_data

    # Store previous values
    analytics_data["previousTrafficLightEfficiency"] = analytics_data["trafficLightEfficiency"]
    analytics_data["previousAverageWaitTime"] = analytics_data["averageWaitTime"]

    # Calculate traffic light efficiency (ratio of green lights to total)
    green_lights = len([light for light in traffic_lights if light["state"] == "green"])
    total_lights = len(traffic_lights)
    if total_lights > 0:
        efficiency = green_lights / total_lights
    else:
        efficiency = 0

    # Add some randomness to make it more dynamic
    efficiency = min(1.0, max(0.0, efficiency + random.uniform(-0.05, 0.05)))
    analytics_data["trafficLightEfficiency"] = efficiency

    # Calculate average wait time at intersections
    # This is simulated based on queue lengths at traffic lights
    total_queue = sum(light["queue_length"] for light in traffic_lights)
    if total_lights > 0:
        avg_queue = total_queue / total_lights
        # Convert queue length to wait time (roughly 5 seconds per vehicle in queue)
        wait_time = avg_queue * 5.0
    else:
        wait_time = 0

    # Add some randomness
    wait_time = max(0.0, wait_time + random.uniform(-1.0, 3.0))
    analytics_data["averageWaitTime"] = wait_time

    # Calculate average speed
    if vehicles:
        avg_speed = sum(v["speed"] for v in vehicles) / len(vehicles)
    else:
        avg_speed = 0

    # Update speed history
    analytics_data["speedHistory"].append(avg_speed)
    if len(analytics_data["speedHistory"]) > 10:
        analytics_data["speedHistory"].pop(0)

    # Calculate congestion level
    # Simulated based on vehicle density and speed
    if vehicles and city_data["edges"]:
        # More vehicles = more congestion
        vehicle_factor = min(1.0, len(vehicles) / (city_data["vehicle_count"] * 2))

        # Slower speeds = more congestion
        speed_factor = 1.0
        if avg_speed > 0:
            # Normalize speed (30 km/h is considered normal)
            speed_factor = max(0.0, min(1.0, 30 / avg_speed))

        congestion = (vehicle_factor * 0.6) + (speed_factor * 0.4)
    else:
        congestion = 0.0

    # Add some randomness
    congestion = min(1.0, max(0.0, congestion + random.uniform(-0.05, 0.05)))

    # Update congestion trend
    analytics_data["congestionTrend"].append(congestion)
    if len(analytics_data["congestionTrend"]) > 10:
        analytics_data["congestionTrend"].pop(0)

    # Calculate incident impact
    if incidents:
        analytics_data["affectedVehicles"] = min(len(vehicles), random.randint(1, 5))
        analytics_data["reroutedVehicles"] = min(analytics_data["affectedVehicles"], random.randint(0, 3))
        analytics_data["averageIncidentDelay"] = random.randint(2, 15)  # 2-15 minutes delay
    else:
        analytics_data["affectedVehicles"] = 0
        analytics_data["reroutedVehicles"] = 0
        analytics_data["averageIncidentDelay"] = 0

    return analytics_data

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

                # Generate congestion levels for each edge
                congestion_levels = {}
                for edge in city_data["edges"]:
                    # Generate a random congestion level between 0 and 1
                    # Higher for edges with more traffic lights nearby
                    base_congestion = random.uniform(0.1, 0.6)

                    # Add some randomness based on time
                    time_factor = (datetime.now().minute % 10) / 10.0
                    congestion = min(1.0, base_congestion + (time_factor * 0.4))

                    congestion_levels[edge["id"]] = congestion

                # Generate updated vehicles with dynamic movement
                vehicles = generate_vehicles_for_city(current_city)

                # Apply smart routing to vehicles
                vehicles = suggest_rerouting(vehicles, city_data, congestion_levels, incidents)

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

                # Optimize traffic light timings based on congestion
                updated_traffic_lights = optimize_traffic_lights(city_data, congestion_levels, city_data["traffic_lights"])

                # Send updated traffic lights
                await websocket.send_json({
                    "type": "traffic_lights",
                    "data": updated_traffic_lights
                })

                # Send congestion levels
                await websocket.send_json({
                    "type": "congestion",
                    "data": congestion_levels
                })

                # Calculate and send analytics data
                current_analytics = calculate_analytics_data(vehicles, updated_traffic_lights, city_data)
                await websocket.send_json({
                    "type": "analytics",
                    "data": current_analytics
                })

                # Generate congestion levels for each edge
                congestion_levels = {}
                for edge in city_data["edges"]:
                    # Generate a random congestion level between 0 and 1
                    # Higher for edges with more traffic lights nearby
                    base_congestion = random.uniform(0.1, 0.6)

                    # Add some randomness based on time
                    time_factor = (datetime.now().minute % 10) / 10.0
                    congestion = min(1.0, base_congestion + (time_factor * 0.4))

                    congestion_levels[edge["id"]] = congestion

                await websocket.send_json({
                    "type": "congestion",
                    "data": congestion_levels
                })

                # Send incidents if any
                if incidents:
                    await websocket.send_json({
                        "type": "incidents",
                        "data": incidents
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

# Incident endpoints
@app.post("/incidents/add")
async def add_incident(incident_data: dict):
    global incidents

    # Extract incident data
    lat = incident_data.get("lat")
    lon = incident_data.get("lon")
    incident_type = incident_data.get("type", "accident")

    if lat is None or lon is None:
        return {
            "status": "error",
            "message": "Latitude and longitude are required",
            "timestamp": datetime.now().isoformat()
        }

    # Generate a unique ID
    incident_id = f"incident_{len(incidents) + 1}"

    # Current timestamp
    current_time = datetime.now().timestamp()

    # Expected clearance time (15-60 minutes from now)
    clearance_time = current_time + random.randint(15 * 60, 60 * 60)

    # Create the incident
    new_incident = {
        "id": incident_id,
        "lat": lat,
        "lon": lon,
        "type": incident_type,
        "timestamp": current_time,
        "expected_clearance": clearance_time,
        "severity": random.choice(["low", "medium", "high"]),
        "status": "active"
    }

    # Add to incidents list
    incidents.append(new_incident)

    # Broadcast to all clients
    await broadcast_message("incidents", incidents)

    return {
        "status": "success",
        "message": f"Incident reported: {incident_type}",
        "timestamp": datetime.now().isoformat(),
        "incident": new_incident
    }

# Route planning endpoint
@app.post("/route/plan")
async def plan_route(route_data: dict):
    global current_city

    # Extract route data
    origin_lat = route_data.get("origin_lat")
    origin_lon = route_data.get("origin_lon")
    destination_lat = route_data.get("destination_lat")
    destination_lon = route_data.get("destination_lon")

    if origin_lat is None or origin_lon is None or destination_lat is None or destination_lon is None:
        return {
            "status": "error",
            "message": "Origin and destination coordinates are required",
            "timestamp": datetime.now().isoformat()
        }

    # Get city data
    city_data = CITY_DATA[current_city]

    # Generate congestion levels
    congestion_levels = {}
    for edge in city_data["edges"]:
        base_congestion = random.uniform(0.1, 0.6)
        time_factor = (datetime.now().minute % 10) / 10.0
        congestion = min(1.0, base_congestion + (time_factor * 0.4))
        congestion_levels[edge["id"]] = congestion

    # Find closest nodes to origin and destination
    origin_node = None
    destination_node = None
    min_origin_distance = float('inf')
    min_dest_distance = float('inf')

    for node in city_data["nodes"]:
        # Calculate distance to origin
        origin_distance = math.sqrt(
            (node["lat"] - origin_lat)**2 +
            (node["lon"] - origin_lon)**2
        )

        # Calculate distance to destination
        dest_distance = math.sqrt(
            (node["lat"] - destination_lat)**2 +
            (node["lon"] - destination_lon)**2
        )

        if origin_distance < min_origin_distance:
            min_origin_distance = origin_distance
            origin_node = node

        if dest_distance < min_dest_distance:
            min_dest_distance = dest_distance
            destination_node = node

    if not origin_node or not destination_node:
        return {
            "status": "error",
            "message": "Could not find suitable nodes for routing",
            "timestamp": datetime.now().isoformat()
        }

    # Build the city graph with congestion
    city_graph = build_city_graph(city_data, congestion_levels)

    # Find the shortest path
    path, travel_time = find_shortest_path(city_graph, origin_node["id"], destination_node["id"])

    if not path:
        return {
            "status": "error",
            "message": "Could not find a path between the specified points",
            "timestamp": datetime.now().isoformat()
        }

    # Convert path to coordinates
    route_coordinates = []
    node_id_to_node = {node["id"]: node for node in city_data["nodes"]}

    for node_id in path:
        node = node_id_to_node[node_id]
        route_coordinates.append({
            "lat": node["lat"],
            "lon": node["lon"],
            "name": node["name"]
        })

    # Calculate ETA
    eta_seconds = travel_time * 60  # Convert minutes to seconds
    eta = datetime.now().timestamp() + eta_seconds

    # Create route response
    route_response = {
        "origin": {
            "lat": origin_lat,
            "lon": origin_lon,
            "node_name": origin_node["name"]
        },
        "destination": {
            "lat": destination_lat,
            "lon": destination_lon,
            "node_name": destination_node["name"]
        },
        "route": route_coordinates,
        "travel_time_minutes": travel_time,
        "eta": eta,
        "distance_km": travel_time / 60 * 30,  # Assuming 30 km/h average speed
        "congestion_factor": sum(congestion_levels.get(edge["id"], 0) for edge in city_data["edges"] if edge["source_id"] in path and edge["target_id"] in path) / max(1, len(path) - 1)
    }

    return {
        "status": "success",
        "message": "Route planned successfully",
        "timestamp": datetime.now().isoformat(),
        "route": route_response
    }

# Vehicle endpoints
@app.post("/vehicles/add")
async def add_vehicle(vehicle_data: dict):
    global current_city, incidents

    # Extract vehicle data
    origin = vehicle_data.get("origin")
    destination = vehicle_data.get("destination")
    vehicle_type = vehicle_data.get("type", "car")

    # New parameters for map-based selection
    origin_lat = vehicle_data.get("origin_lat")
    origin_lon = vehicle_data.get("origin_lon")
    destination_lat = vehicle_data.get("destination_lat")
    destination_lon = vehicle_data.get("destination_lon")

    # Get city data
    city_data = CITY_DATA[current_city]

    # Find origin and destination nodes
    origin_node = None
    destination_node = None

    # If coordinates are provided, find the closest nodes
    if origin_lat is not None and origin_lon is not None:
        min_distance = float('inf')
        for node in city_data["nodes"]:
            distance = math.sqrt(
                (node["lat"] - origin_lat)**2 +
                (node["lon"] - origin_lon)**2
            )
            if distance < min_distance:
                min_distance = distance
                origin_node = node

    if destination_lat is not None and destination_lon is not None:
        min_distance = float('inf')
        for node in city_data["nodes"]:
            distance = math.sqrt(
                (node["lat"] - destination_lat)**2 +
                (node["lon"] - destination_lon)**2
            )
            if distance < min_distance:
                min_distance = distance
                destination_node = node

    # If names are provided, find the nodes by name
    if not origin_node and origin:
        for node in city_data["nodes"]:
            if node["name"] == origin:
                origin_node = node
                break

    if not destination_node and destination:
        for node in city_data["nodes"]:
            if node["name"] == destination:
                destination_node = node
                break

    if not origin_node or not destination_node:
        return {
            "status": "error",
            "message": "Invalid origin or destination",
            "timestamp": datetime.now().isoformat()
        }

    # Generate congestion levels
    congestion_levels = {}
    for edge in city_data["edges"]:
        base_congestion = random.uniform(0.1, 0.6)
        time_factor = (datetime.now().minute % 10) / 10.0
        congestion = min(1.0, base_congestion + (time_factor * 0.4))
        congestion_levels[edge["id"]] = congestion

    # Build the city graph with congestion
    city_graph = build_city_graph(city_data, congestion_levels)

    # Find the shortest path
    path, travel_time = find_shortest_path(city_graph, origin_node["id"], destination_node["id"])

    if not path:
        return {
            "status": "error",
            "message": "Could not find a path between the specified points",
            "timestamp": datetime.now().isoformat()
        }

    # Convert path to coordinates
    route_coordinates = []
    node_id_to_node = {node["id"]: node for node in city_data["nodes"]}

    for node_id in path:
        node = node_id_to_node[node_id]
        route_coordinates.append({
            "lat": node["lat"],
            "lon": node["lon"]
        })

    # Generate a unique ID
    vehicle_id = f"{current_city.lower().replace(' ', '_')}_custom_{datetime.now().strftime('%H%M%S')}"

    # Generate random speed based on vehicle type
    base_speed = 25 if vehicle_type == "car" else (20 if vehicle_type == "bus" else 15)
    speed = base_speed + random.uniform(-5, 10)

    # Calculate ETA based on travel time from routing
    eta = datetime.now().timestamp() + (travel_time * 60)  # Convert minutes to seconds

    # Create the vehicle with optimized route
    new_vehicle = {
        "id": vehicle_id,
        "type": vehicle_type,
        "lat": origin_node["lat"],
        "lon": origin_node["lon"],
        "origin": origin_node["name"],
        "destination": destination_node["name"],
        "speed": speed,
        "status": "moving",
        "eta": eta,
        "current_route": route_coordinates
    }

    # Check if the route passes near any incidents
    for incident in incidents:
        for point in route_coordinates:
            incident_distance = math.sqrt(
                (point["lat"] - incident["lat"])**2 +
                (point["lon"] - incident["lon"])**2
            )

            # If route passes near an incident, mark as affected and add delay
            if incident_distance < 0.01:  # Approximately 1km
                new_vehicle["status"] = "affected_by_incident"
                new_vehicle["eta"] += random.randint(300, 900)  # 5-15 minutes delay
                break

    # Generate a new set of vehicles including this one
    vehicles = generate_vehicles_for_city(current_city)
    vehicles.append(new_vehicle)

    # Broadcast to all clients
    await broadcast_message("vehicles", vehicles)

    return {
        "status": "success",
        "message": f"Vehicle added: {vehicle_type} with optimized route",
        "timestamp": datetime.now().isoformat(),
        "vehicle": new_vehicle,
        "route_details": {
            "path": [node_id_to_node[node_id]["name"] for node_id in path],
            "travel_time_minutes": travel_time,
            "distance_km": travel_time / 60 * 30  # Assuming 30 km/h average speed
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Use a different port
        log_level="info"
    )
