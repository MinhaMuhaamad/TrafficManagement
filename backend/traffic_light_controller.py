import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from city_graph import CityGraph

class TrafficLight:
    def __init__(self, node_id: Any, lat: float, lon: float):
        """
        Initialize a traffic light at an intersection.
        
        Args:
            node_id: ID of the node in the city graph
            lat: Latitude of the traffic light
            lon: Longitude of the traffic light
        """
        self.id = str(node_id)
        self.node_id = node_id
        self.lat = lat
        self.lon = lon
        self.state = "red"  # red, green, yellow
        self.duration = {
            "red": random.randint(20, 40),
            "green": random.randint(15, 30),
            "yellow": 5
        }
        self.last_change = time.time()
        self.next_change = self.last_change + self.duration[self.state]
        self.queue_length = 0
        self.incoming_edges = []
        self.outgoing_edges = []
    
    def update(self, current_time: float = None) -> None:
        """
        Update the traffic light state based on time.
        
        Args:
            current_time: Current time (defaults to time.time())
        """
        if current_time is None:
            current_time = time.time()
        
        if current_time >= self.next_change:
            # Change state
            if self.state == "red":
                self.state = "green"
            elif self.state == "green":
                self.state = "yellow"
            elif self.state == "yellow":
                self.state = "red"
            
            # Update timing
            self.last_change = current_time
            self.next_change = current_time + self.duration[self.state]
    
    def optimize_timing(self, queue_length: int) -> None:
        """
        Optimize traffic light timing based on queue length.
        
        Args:
            queue_length: Number of vehicles waiting at the light
        """
        self.queue_length = queue_length
        
        # Adjust green light duration based on queue length
        # Longer queues get longer green lights
        if queue_length > 10:
            self.duration["green"] = min(45, 15 + queue_length)
        elif queue_length > 5:
            self.duration["green"] = min(30, 15 + queue_length / 2)
        else:
            self.duration["green"] = 15
        
        # Adjust red light duration inversely
        self.duration["red"] = max(15, 40 - queue_length)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "node_id": self.node_id,
            "lat": self.lat,
            "lon": self.lon,
            "state": self.state,
            "last_change": self.last_change,
            "next_change": self.next_change,
            "queue_length": self.queue_length
        }


class TrafficLightController:
    def __init__(self, city_graph: CityGraph):
        """
        Initialize the traffic light controller.
        
        Args:
            city_graph: City graph object
        """
        self.city_graph = city_graph
        self.traffic_lights = {}
        
        # Create traffic lights at intersections
        self._create_traffic_lights()
    
    def _create_traffic_lights(self) -> None:
        """Create traffic lights at intersections"""
        for node in self.city_graph.nodes:
            # Check if it's an intersection (more than 2 connected edges)
            if node['is_intersection']:
                # Create a traffic light
                traffic_light = TrafficLight(
                    node_id=node['id'],
                    lat=node['lat'],
                    lon=node['lon']
                )
                
                # Find incoming and outgoing edges
                for edge in self.city_graph.edges:
                    if edge['target'] == node['id']:
                        traffic_light.incoming_edges.append(edge['id'])
                    elif edge['source'] == node['id']:
                        traffic_light.outgoing_edges.append(edge['id'])
                
                # Add to dictionary
                self.traffic_lights[node['id']] = traffic_light
    
    def update(self) -> None:
        """Update all traffic lights"""
        current_time = time.time()
        
        for light in self.traffic_lights.values():
            light.update(current_time)
    
    def optimize_traffic_lights(self, edge_vehicle_counts: Dict[str, int]) -> None:
        """
        Optimize traffic light timings based on vehicle counts.
        
        Args:
            edge_vehicle_counts: Dictionary of edge IDs to vehicle counts
        """
        for light in self.traffic_lights.values():
            # Calculate queue length as sum of vehicles on incoming edges
            queue_length = sum(edge_vehicle_counts.get(edge_id, 0) 
                              for edge_id in light.incoming_edges)
            
            # Optimize timing based on queue length
            light.optimize_timing(queue_length)
    
    def get_traffic_light(self, node_id: Any) -> Optional[TrafficLight]:
        """Get a traffic light by node ID"""
        return self.traffic_lights.get(node_id)
    
    def get_traffic_lights(self) -> List[Dict[str, Any]]:
        """Get all traffic lights as dictionaries"""
        return [light.to_dict() for light in self.traffic_lights.values()]
    
    def dynamic_programming_optimization(self) -> None:
        """
        Use dynamic programming to optimize traffic light timings.
        This is a simplified implementation of the dynamic programming approach.
        """
        # For each traffic light
        for light_id, light in self.traffic_lights.items():
            # Skip if queue is very short
            if light.queue_length < 3:
                continue
            
            # Get neighboring traffic lights
            neighboring_lights = []
            for edge_id in light.outgoing_edges:
                edge = self.city_graph.get_edge_by_id(edge_id)
                if edge and edge['target'] in self.traffic_lights:
                    neighboring_lights.append(self.traffic_lights[edge['target']])
            
            # Skip if no neighbors
            if not neighboring_lights:
                continue
            
            # Calculate optimal green time based on queue and neighbors
            # This is a simplified version of dynamic programming
            # In a real system, we would use a more complex model
            
            # Base green time from queue length
            base_green_time = min(45, 15 + light.queue_length)
            
            # Adjust based on downstream traffic lights
            downstream_factor = 1.0
            for neighbor in neighboring_lights:
                # If neighbor has a long queue, reduce our green time
                if neighbor.queue_length > 10:
                    downstream_factor *= 0.9
                # If neighbor is green, increase our green time to create a "green wave"
                if neighbor.state == "green":
                    downstream_factor *= 1.1
            
            # Apply the factor
            optimal_green_time = max(15, min(60, base_green_time * downstream_factor))
            
            # Update the light duration
            light.duration["green"] = optimal_green_time
            
            # Adjust red time inversely but ensure minimum safety time
            light.duration["red"] = max(15, 60 - optimal_green_time)
