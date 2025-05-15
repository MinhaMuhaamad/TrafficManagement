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
        
        # For dynamic programming optimization
        self.optimal_durations = {}
        self.state_history = []
        self.queue_history = []
        
        # For manual control
        self.control_mode = "auto"  # auto, manual
        self.manual_duration = 60  # How long manual control lasts
        self.manual_start_time = 0
    
    def update(self, current_time: float = None) -> None:
        """
        Update the traffic light state based on time.
        
        Args:
            current_time: Current time (defaults to time.time())
        """
        if current_time is None:
            current_time = time.time()
            
        # If in manual mode, check if we should revert to auto
        if self.control_mode == "manual" and current_time - self.manual_start_time > self.manual_duration:
            self.control_mode = "auto"
            
        # Only auto-change state if in auto mode
        if self.control_mode == "auto" and current_time >= self.next_change:
            # Record state before changing
            self.state_history.append({
                "state": self.state,
                "duration": current_time - self.last_change,
                "queue_length": self.queue_length,
                "timestamp": current_time
            })
            
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
    
    def set_state(self, new_state: str, current_time: float = None) -> None:
        """
        Manually set the traffic light state.
        
        Args:
            new_state: New state (red, green, yellow)
            current_time: Current time (defaults to time.time())
        """
        if current_time is None:
            current_time = time.time()
            
        if new_state not in ["red", "green", "yellow"]:
            return
            
        # Set to manual control mode
        self.control_mode = "manual"
        self.manual_start_time = current_time
        
        # Record state before changing
        self.state_history.append({
            "state": self.state,
            "duration": current_time - self.last_change,
            "queue_length": self.queue_length,
            "timestamp": current_time,
            "manual": True
        })
        
        # Change state
        self.state = new_state
        self.last_change = current_time
        self.next_change = current_time + self.duration[self.state]
    
    def optimize_timing(self, queue_length: int) -> None:
        """
        Optimize traffic light timing based on queue length.
        
        Args:
            queue_length: Number of vehicles waiting at the light
        """
        # Record queue length
        self.queue_history.append({
            "queue_length": queue_length,
            "timestamp": time.time()
        })
        
        self.queue_length = queue_length
        
        # Only optimize if in auto mode
        if self.control_mode != "auto":
            return
        
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
            "queue_length": self.queue_length,
            "control_mode": self.control_mode
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
        
        # For dynamic programming
        self.optimization_interval = 60  # Optimize every 60 seconds
        self.last_optimization = time.time()
        self.optimization_state = {}
        
        # Control mode
        self.control_mode = "auto"  # auto, dynamic_programming, manual
    
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
            
        # Run dynamic programming optimization if in that mode
        if self.control_mode == "dynamic_programming" and current_time - self.last_optimization > self.optimization_interval:
            self.dynamic_programming_optimization()
            self.last_optimization = current_time
    
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
    
    def set_traffic_light_state(self, node_id: Any, state: str) -> bool:
        """
        Set the state of a traffic light manually.
        
        Args:
            node_id: ID of the node with the traffic light
            state: New state (red, green, yellow)
            
        Returns:
            True if successful, False otherwise
        """
        light = self.get_traffic_light(node_id)
        if not light:
            return False
            
        light.set_state(state)
        return True
    
    def set_control_mode(self, mode: str) -> bool:
        """
        Set the control mode for all traffic lights.
        
        Args:
            mode: Control mode (auto, dynamic_programming, manual)
            
        Returns:
            True if successful, False otherwise
        """
        if mode not in ["auto", "dynamic_programming", "manual"]:
            return False
            
        self.control_mode = mode
        return True
    
    def dynamic_programming_optimization(self) -> None:
        """
        Use dynamic programming to optimize traffic light timings.
        This is a more sophisticated implementation of the dynamic programming approach.
        """
        # Skip if not in dynamic programming mode
        if self.control_mode != "dynamic_programming":
            return
            
        # Initialize optimization state if needed
        if not self.optimization_state:
            self.optimization_state = {
                light_id: {
                    "value_function": {"red": 0, "green": 0, "yellow": 0},
                    "policy": {"red": "green", "green": "yellow", "yellow": "red"},
                    "state_transitions": []
                } for light_id in self.traffic_lights
            }
        
        # For each traffic light
        for light_id, light in self.traffic_lights.items():
            # Skip if queue is very short
            if light.queue_length :
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
            
            # Get state history
            state_history = light.state_history[-10:] if light.state_history else []
            
            # Calculate rewards for each state
            rewards = {
                "red": -light.queue_length,  # Negative reward proportional to queue length
                "green": 5 - 0.2 * light.queue_length,  # Positive reward, reduced by queue
                "yellow": -2  # Small negative reward for yellow (transition state)
            }
            
            # Calculate value function using Bellman equation
            # V(s) = R(s) + gamma * max_a sum_s' P(s'|s,a) * V(s')
            gamma = 0.9  # Discount factor
            
            # Update value function
            for state in ["red", "green", "yellow"]:
                # Get next state based on policy
                next_state = self.optimization_state[light_id]["policy"][state]
                
                # Calculate value
                value = rewards[state] + gamma * self.optimization_state[light_id]["value_function"][next_state]
                
                # Update value function
                self.optimization_state[light_id]["value_function"][state] = value
            
            # Update policy based on value function
            for state in ["red", "green", "yellow"]:
                # Standard transitions
                possible_next_states = {
                    "red": ["green"],
                    "green": ["yellow"],
                    "yellow": ["red"]
                }
                
                # Find action that maximizes value
                best_value = float('-inf')
                best_next_state = None
                
                for next_state in possible_next_states[state]:
                    value = rewards[state] + gamma * self.optimization_state[light_id]["value_function"][next_state]
                    
                    if value > best_value:
                        best_value = value
                        best_next_state = next_state
                
                # Update policy
                if best_next_state:
                    self.optimization_state[light_id]["policy"][state] = best_next_state
            
            # Calculate optimal durations based on queue and value function
            optimal_durations = {
                "red": max(15, 30 - light.queue_length),
                "green": min(45, 15 + light.queue_length),
                "yellow": 5  # Fixed for safety
            }
            
            # Adjust for neighboring lights to create "green waves"
            green_neighbors = sum(1 for neighbor in neighboring_lights if neighbor.state == "green")
            if green_neighbors > 0 and light.state == "red":
                # Reduce red duration if downstream lights are green
                optimal_durations["red"] = max(10, optimal_durations["red"] - 5 * green_neighbors)
            
            # Update light durations
            light.duration = optimal_durations
            
            # Record transition for learning
            self.optimization_state[light_id]["state_transitions"].append({
                "from_state": light.state,
                "queue_length": light.queue_length,
                "optimal_duration": optimal_durations[light.state],
                "timestamp": time.time()
            })
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data for traffic light controller"""
        total_queue = sum(light.queue_length for light in self.traffic_lights.values())
        avg_queue = total_queue / max(1, len(self.traffic_lights))
        
        green_lights = sum(1 for light in self.traffic_lights.values() if light.state == "green")
        red_lights = sum(1 for light in self.traffic_lights.values() if light.state == "red")
        
        # Calculate efficiency (ratio of green to total, weighted by queue lengths)
        green_queue = sum(light.queue_length for light in self.traffic_lights.values() if light.state == "green")
        efficiency = green_queue / max(1, total_queue) if total_queue > 0 else 0
        
        return {
            "total_lights": len(self.traffic_lights),
            "green_lights": green_lights,
            "red_lights": red_lights,
            "total_queue": total_queue,
            "avg_queue": avg_queue,
            "efficiency": efficiency,
            "control_mode": self.control_mode
        }
