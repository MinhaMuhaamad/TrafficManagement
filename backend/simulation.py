import time
import random
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
from city_graph import CityGraph
from traffic_light_controller import TrafficLightController
from vehicle_router import VehicleRouter

class Simulation:
    def __init__(self, city_graph: CityGraph, traffic_light_controller: TrafficLightController, vehicle_router: VehicleRouter):
        """
        Initialize the simulation.
        
        Args:
            city_graph: City graph object
            traffic_light_controller: Traffic light controller
            vehicle_router: Vehicle router
        """
        self.city_graph = city_graph
        self.traffic_light_controller = traffic_light_controller
        self.vehicle_router = vehicle_router
        
        self.is_running = False
        self.last_update_time = 0
        self.incidents = {}  # Dictionary of incident ID to incident data
        
        # Simulation parameters
        self.vehicle_spawn_rate = 0.2  # Vehicles per second
        self.incident_probability = 0.001  # Probability of incident per second
        self.max_vehicles = 50  # Maximum number of vehicles
        
        # Simulation thread
        self.simulation_thread = None
        
        # Analytics data
        self.analytics = {
            "start_time": 0,
            "elapsed_time": 0,
            "vehicle_count_history": [],
            "congestion_trend": [],
            "traffic_light_efficiency": 0,
            "previous_traffic_light_efficiency": 0,
            "average_wait_time": 0,
            "previous_average_wait_time": 0,
            "affected_vehicles": 0,
            "rerouted_vehicles": 0,
            "average_incident_delay": 0,
            "traffic_light_optimization_status": "Active",
            "route_optimization_status": "Active",
            "congestion_management_status": "Active",
            "speed_history": []
        }
        
        # Update interval for analytics
        self.analytics_update_interval = 10  # seconds
        self.last_analytics_update = 0
    
    def start(self) -> None:
        """Start the simulation"""
        if self.is_running:
            return
        
        self.is_running = True
        self.last_update_time = time.time()
        self.analytics["start_time"] = time.time()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def stop(self) -> None:
        """Stop the simulation"""
        self.is_running = False
        
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
            self.simulation_thread = None
    
    def _simulation_loop(self) -> None:
        """Main simulation loop"""
        while self.is_running:
            self.update()
            time.sleep(0.1)  # Sleep to avoid high CPU usage
    
    def update(self) -> None:
        """Update the simulation state"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update analytics
        self.analytics["elapsed_time"] = current_time - self.analytics["start_time"]
        
        # Spawn new vehicles
        self._spawn_vehicles(delta_time)
        
        # Generate random incidents
        self._generate_incidents(delta_time)
        
        # Update incidents (clear expired ones)
        self._update_incidents(current_time)
        
        # Update vehicle positions
        self.vehicle_router.update(delta_time)
        
        # Update traffic lights
        self.traffic_light_controller.update()
        
        # Optimize traffic lights based on vehicle counts
        self.traffic_light_controller.optimize_traffic_lights(
            self.vehicle_router.get_edge_vehicle_counts()
        )
        
        # Use dynamic programming for traffic light optimization if in that mode
        if self.traffic_light_controller.control_mode == "dynamic_programming":
            self.traffic_light_controller.dynamic_programming_optimization()
            
        # Use multi-vehicle routing optimization
        self.vehicle_router.optimize_multi_vehicle_routing()
        
        # Update analytics periodically
        if current_time - self.last_analytics_update > self.analytics_update_interval:
            self._update_analytics()
            self.last_analytics_update = current_time
    
    def _spawn_vehicles(self, delta_time: float) -> None:
        """
        Spawn new vehicles based on spawn rate.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Calculate number of vehicles to spawn
        num_to_spawn = int(self.vehicle_spawn_rate * delta_time)
        
        # Add random chance for fractional part
        if random.random() < (self.vehicle_spawn_rate * delta_time - num_to_spawn):
            num_to_spawn += 1
        
        # Check if we're under the maximum
        current_vehicle_count = len(self.vehicle_router.vehicles)
        num_to_spawn = min(num_to_spawn, self.max_vehicles - current_vehicle_count)
        
        # Spawn vehicles
        for _ in range(num_to_spawn):
            # Randomly choose vehicle type
            vehicle_type = random.choices(
                ["car", "bus", "truck"],
                weights=[0.8, 0.15, 0.05],
                k=1
            )[0]
            
            self.vehicle_router.add_vehicle(vehicle_type=vehicle_type)
    
    def _generate_incidents(self, delta_time: float) -> None:
        """
        Generate random incidents based on probability.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Calculate probability of incident in this time step
        incident_chance = self.incident_probability * delta_time
        
        if random.random() < incident_chance:
            # Generate a random incident
            edge = self.city_graph.get_random_edge()
            
            # Choose a random point along the edge
            progress = random.random()
            lat = edge['source_lat'] + progress * (edge['target_lat'] - edge['source_lat'])
            lon = edge['source_lon'] + progress * (edge['target_lon'] - edge['source_lon'])
            
            # Choose incident type
            incident_type = random.choice(["accident", "congestion", "construction"])
            
            # Add the incident
            self.add_incident(lat, lon, incident_type)
    
    def add_incident(self, lat: float, lon: float, incident_type: str) -> str:
        """
        Add an incident to the simulation.
        
        Args:
            lat: Latitude of the incident
            lon: Longitude of the incident
            incident_type: Type of incident (accident, congestion, etc.)
        
        Returns:
            Incident ID
        """
        # Generate a unique ID
        incident_id = str(uuid.uuid4())[:8]
        
        # Find the nearest edge
        nearest_edge = None
        min_distance = float('inf')
        
        for edge in self.city_graph.edges:
            # Calculate distance to edge (simplified as distance to midpoint)
            edge_mid_lat = (edge['source_lat'] + edge['target_lat']) / 2
            edge_mid_lon = (edge['source_lon'] + edge['target_lon']) / 2
            
            distance = ((lat - edge_mid_lat) ** 2 + (lon - edge_mid_lon) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_edge = edge
        
        if not nearest_edge:
            return None
        
        # Calculate duration based on type
        if incident_type == "accident":
            duration = random.randint(300, 900)  # 5-15 minutes
        elif incident_type == "congestion":
            duration = random.randint(180, 600)  # 3-10 minutes
        elif incident_type == "construction":
            duration = random.randint(600, 1800)  # 10-30 minutes
        else:
            duration = random.randint(60, 300)  # 1-5 minutes
        
        # Create incident
        incident = {
            "id": incident_id,
            "lat": lat,
            "lon": lon,
            "type": incident_type,
            "edge_id": nearest_edge['id'],
            "timestamp": time.time(),
            "duration": duration,
            "expected_clearance": time.time() + duration
        }
        
        # Add to dictionary
        self.incidents[incident_id] = incident
        
        # Update edge congestion
        if incident_type == "accident":
            # Accidents cause severe congestion
            self.city_graph.update_edge_congestion(nearest_edge['id'], 0.9)
        elif incident_type == "congestion":
            # Congestion incidents increase existing congestion
            current_congestion = nearest_edge.get('congestion', 0)
            self.city_graph.update_edge_congestion(nearest_edge['id'], min(1.0, current_congestion + 0.5))
        elif incident_type == "construction":
            # Construction causes moderate congestion
            self.city_graph.update_edge_congestion(nearest_edge['id'], 0.7)
        
        # Reroute affected vehicles
        affected_count = self.vehicle_router.reroute_vehicles([nearest_edge['id']])
        
        # Update analytics
        self.analytics["affected_vehicles"] += affected_count
        
        return incident_id
    
    def _update_incidents(self, current_time: float) -> None:
        """
        Update incidents and clear expired ones.
        
        Args:
            current_time: Current time
        """
        # Check for expired incidents
        expired_incidents = []
        
        for incident_id, incident in self.incidents.items():
            if current_time >= incident['expected_clearance']:
                expired_incidents.append(incident_id)
        
        # Clear expired incidents
        for incident_id in expired_incidents:
            incident = self.incidents[incident_id]
            
            # Reset edge congestion
            edge = self.city_graph.get_edge_by_id(incident['edge_id'])
            if edge:
                # Gradually reduce congestion rather than immediately clearing it
                current_congestion = edge.get('congestion', 0)
                self.city_graph.update_edge_congestion(incident['edge_id'], max(0, current_congestion - 0.5))
            
            # Remove incident
            del self.incidents[incident_id]
    
    def get_incidents(self) -> List[Dict[str, Any]]:
        """Get all incidents as dictionaries"""
        return list(self.incidents.values())
    
    def get_congestion_levels(self) -> Dict[str, float]:
        """Get congestion levels for all edges"""
        congestion_levels = {}
        
        for edge in self.city_graph.edges:
            congestion_levels[edge['id']] = edge['congestion']
        
        return congestion_levels
        
    def _update_analytics(self) -> None:
        """Update analytics data"""
        # Vehicle count history
        self.analytics["vehicle_count_history"].append({
            "timestamp": time.time(),
            "count": len(self.vehicle_router.vehicles)
        })
        
        # Congestion trend
        avg_congestion = 0
        if self.city_graph.edges:
            avg_congestion = sum(edge['congestion'] for edge in self.city_graph.edges) / len(self.city_graph.edges)
        
        self.analytics["congestion_trend"].append(avg_congestion)
        
        # Traffic light efficiency
        traffic_light_analytics = self.traffic_light_controller.get_analytics()
        self.analytics["previous_traffic_light_efficiency"] = self.analytics["traffic_light_efficiency"]
        self.analytics["traffic_light_efficiency"] = traffic_light_analytics["efficiency"]
        
        # Average wait time
        total_wait_time = 0
        count = 0
        
        for light in self.traffic_light_controller.traffic_lights.values():
            if light.state == "red" and light.queue_length > 0:
                # Estimate wait time based on remaining red time and queue length
                remaining_time = light.next_change - time.time()
                wait_time = remaining_time * (1 + 0.1 * light.queue_length)  # Longer queues wait longer
                total_wait_time += wait_time
                count += 1
        
        self.analytics["previous_average_wait_time"] = self.analytics["average_wait_time"]
        self.analytics["average_wait_time"] = total_wait_time / max(1, count) if count > 0 else 0
        
        # Vehicle router analytics
        vehicle_analytics = self.vehicle_router.get_analytics()
        self.analytics["rerouted_vehicles"] = vehicle_analytics["total_reroutes"]
        
        # Average speed
        avg_speed = 0
        if self.vehicle_router.vehicles:
            avg_speed = sum(v.speed for v in self.vehicle_router.vehicles.values()) / len(self.vehicle_router.vehicles)
        
        self.analytics["speed_history"].append(avg_speed)
        
        # Average incident delay
        if self.incidents:
            total_delay = 0
            for incident in self.incidents.values():
                delay = incident["expected_clearance"] - incident["timestamp"]
                total_delay += delay
            
            self.analytics["average_incident_delay"] = total_delay / len(self.incidents) / 60  # Convert to minutes
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data"""
        return self.analytics
    
    def set_traffic_light_control_mode(self, mode: str) -> bool:
        """
        Set the traffic light control mode.
        
        Args:
            mode: Control mode (auto, dynamic_programming, manual)
            
        Returns:
            True if successful, False otherwise
        """
        return self.traffic_light_controller.set_control_mode(mode)
    
    def control_traffic_light(self, node_id: str, state: str) -> bool:
        """
        Control a specific traffic light.
        
        Args:
            node_id: ID of the node with the traffic light
            state: New state (red, green, yellow)
            
        Returns:
            True if successful, False otherwise
        """
        return self.traffic_light_controller.set_traffic_light_state(node_id, state)
    
    def add_vehicle(self, origin: str = None, destination: str = None, vehicle_type: str = "car") -> str:
        """
        Add a vehicle to the simulation.
        
        Args:
            origin: Origin node ID (random if None)
            destination: Destination node ID (random if None)
            vehicle_type: Type of vehicle (car, bus, truck)
            
        Returns:
            Vehicle ID
        """
        return self.vehicle_router.add_vehicle(origin, destination, vehicle_type)

    def is_running(self) -> bool:
        """Return whether the simulation is running."""
        return self.is_running
