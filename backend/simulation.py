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
    
    def start(self) -> None:
        """Start the simulation"""
        if self.is_running:
            return
        
        self.is_running = True
        self.last_update_time = time.time()
        
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
        
        # Use dynamic programming for traffic light optimization
        self.traffic_light_controller.dynamic_programming_optimization()
    
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
            self.vehicle_router.add_vehicle()
    
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
            incident_type = random.choice(["accident", "congestion"])
            
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
        
        # Reroute affected vehicles
        self.vehicle_router.reroute_vehicles([nearest_edge['id']])
        
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
    
    def enhanced_incident_handling(self, incident: Dict[str, Any]) -> None:
        """Enhanced incident handling with severity levels and impact analysis"""
        # Classify incident severity
        severity = self._classify_incident_severity(incident)
        
        # Calculate impact radius
        impact_radius = self._calculate_impact_radius(incident, severity)
        
        # Identify affected roads and intersections
        affected_area = self._identify_affected_area(incident, impact_radius)
        
        # Calculate congestion ripple effect
        congestion_spread = self._calculate_congestion_spread(affected_area)
        
        # Update traffic patterns
        self._update_traffic_patterns(affected_area, congestion_spread)
        
        # Emergency response routing
        if severity > 0.7:  # High severity
            self._coordinate_emergency_response(incident)
