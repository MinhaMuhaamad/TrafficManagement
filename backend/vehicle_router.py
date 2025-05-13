import random
import time
import heapq
import uuid
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from city_graph import CityGraph

class Vehicle:
    def __init__(self, vehicle_id: str, origin_node: Any, destination_node: Any, city_graph: CityGraph):
        """
        Initialize a vehicle with origin and destination.
        
        Args:
            vehicle_id: Unique ID for the vehicle
            origin_node: Starting node ID
            destination_node: Destination node ID
            city_graph: City graph object
        """
        self.id = vehicle_id
        self.origin_node = origin_node
        self.destination_node = destination_node
        
        # Get node objects
        origin_node_obj = city_graph.get_node_by_id(origin_node)
        destination_node_obj = city_graph.get_node_by_id(destination_node)
        
        # Store origin and destination names/coordinates
        self.origin = f"Node {origin_node}"
        self.destination = f"Node {destination_node}"
        
        if origin_node_obj:
            self.origin_lat = origin_node_obj['lat']
            self.origin_lon = origin_node_obj['lon']
        else:
            self.origin_lat = 0
            self.origin_lon = 0
        
        if destination_node_obj:
            self.destination_lat = destination_node_obj['lat']
            self.destination_lon = destination_node_obj['lon']
        else:
            self.destination_lat = 0
            self.destination_lon = 0
        
        # Current position
        self.current_node = origin_node
        self.lat = self.origin_lat
        self.lon = self.origin_lon
        
        # Route and progress
        self.current_route = []  # List of nodes
        self.current_route_edges = []  # List of edges
        self.route_progress = 0  # Index in current_route
        self.edge_progress = 0.0  # Progress along current edge (0-1)
        
        # Timing
        self.start_time = time.time()
        self.eta = 0  # Estimated time of arrival
        
        # Status
        self.status = "waiting"  # waiting, moving, arrived
    
    def calculate_route(self, city_graph: CityGraph) -> None:
        """
        Calculate the shortest route from current position to destination.
        
        Args:
            city_graph: City graph object
        """
        # Use Dijkstra's algorithm to find shortest path
        path = city_graph.get_shortest_path(self.current_node, self.destination_node)
        
        if not path:
            # No path found, stay at current position
            self.status = "stuck"
            return
        
        # Convert path to list of nodes with coordinates
        self.current_route = city_graph.get_path_with_nodes(path)
        
        # Calculate edges along the route
        self.current_route_edges = []
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Find the edge between these nodes
            for edge in city_graph.edges:
                if edge['source'] == source and edge['target'] == target:
                    self.current_route_edges.append(edge)
                    break
        
        # Reset progress
        self.route_progress = 0
        self.edge_progress = 0.0
        
        # Calculate ETA
        self.calculate_eta()
        
        # Update status
        self.status = "moving"
    
    def calculate_eta(self) -> None:
        """Calculate estimated time of arrival"""
        # Sum up travel times for remaining edges
        remaining_time = 0
        
        for i in range(self.route_progress, len(self.current_route_edges)):
            edge = self.current_route_edges[i]
            
            if i == self.route_progress:
                # For current edge, only count remaining portion
                remaining_time += edge['travel_time'] * (1 - self.edge_progress)
            else:
                # For future edges, count full travel time
                remaining_time += edge['travel_time']
        
        # Set ETA
        self.eta = time.time() + remaining_time
    
    def update_position(self, delta_time: float) -> None:
        """
        Update vehicle position based on elapsed time.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        if self.status != "moving" or self.route_progress >= len(self.current_route_edges):
            return
        
        # Get current edge
        current_edge = self.current_route_edges[self.route_progress]
        
        # Calculate progress along edge
        edge_travel_time = current_edge['travel_time']
        progress_increment = delta_time / edge_travel_time
        
        # Update edge progress
        self.edge_progress += progress_increment
        
        # Check if we've reached the end of the edge
        if self.edge_progress >= 1.0:
            # Move to next edge
            self.route_progress += 1
            self.edge_progress = 0.0
            
            # Update current node
            if self.route_progress < len(self.current_route):
                self.current_node = self.current_route[self.route_progress]['id']
            
            # Check if we've reached the destination
            if self.route_progress >= len(self.current_route_edges):
                self.status = "arrived"
                self.lat = self.destination_lat
                self.lon = self.destination_lon
                return
        
        # Interpolate position along current edge
        if self.route_progress < len(self.current_route_edges):
            current_edge = self.current_route_edges[self.route_progress]
            
            # Linear interpolation between source and target
            self.lat = current_edge['source_lat'] + self.edge_progress * (current_edge['target_lat'] - current_edge['source_lat'])
            self.lon = current_edge['source_lon'] + self.edge_progress * (current_edge['target_lon'] - current_edge['source_lon'])
        
        # Recalculate ETA
        self.calculate_eta()
    
    def reroute(self, city_graph: CityGraph) -> None:
        """
        Recalculate route based on current traffic conditions.
        
        Args:
            city_graph: City graph object
        """
        # Save current position
        current_lat = self.lat
        current_lon = self.lon
        
        # Find nearest node to current position
        self.current_node = city_graph.get_nearest_node(current_lat, current_lon)
        
        # Recalculate route
        self.calculate_route(city_graph)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        # Convert route to list of points for frontend
        route_points = []
        for node in self.current_route:
            route_points.append({
                "lat": node['lat'],
                "lon": node['lon']
            })
        
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "lat": self.lat,
            "lon": self.lon,
            "status": self.status,
            "eta": self.eta * 1000,  # Convert to milliseconds for JS
            "current_route": route_points
        }


class VehicleRouter:
    def __init__(self, city_graph: CityGraph):
        """
        Initialize the vehicle router.
        
        Args:
            city_graph: City graph object
        """
        self.city_graph = city_graph
        self.vehicles = {}  # Dictionary of vehicle ID to Vehicle object
        self.edge_vehicle_counts = {}  # Dictionary of edge ID to vehicle count
        
        # Initialize edge vehicle counts
        for edge in city_graph.edges:
            self.edge_vehicle_counts[edge['id']] = 0
    
    def add_vehicle(self, origin_node: Any = None, destination_node: Any = None) -> str:
        """
        Add a new vehicle to the simulation.
        
        Args:
            origin_node: Starting node ID (random if None)
            destination_node: Destination node ID (random if None)
        
        Returns:
            Vehicle ID
        """
        # Generate a unique ID
        vehicle_id = str(uuid.uuid4())[:8]
        
        # If origin or destination not specified, choose random nodes
        if origin_node is None:
            origin_node = self.city_graph.get_random_node()
        
        if destination_node is None:
            # Keep trying until we get a different node
            while True:
                destination_node = self.city_graph.get_random_node()
                if destination_node != origin_node:
                    break
        
        # Create the vehicle
        vehicle = Vehicle(
            vehicle_id=vehicle_id,
            origin_node=origin_node,
            destination_node=destination_node,
            city_graph=self.city_graph
        )
        
        # Calculate initial route
        vehicle.calculate_route(self.city_graph)
        
        # Add to dictionary
        self.vehicles[vehicle_id] = vehicle
        
        # Update edge vehicle counts
        self._update_edge_vehicle_counts()
        
        return vehicle_id
    
    def remove_vehicle(self, vehicle_id: str) -> None:
        """
        Remove a vehicle from the simulation.
        
        Args:
            vehicle_id: Vehicle ID to remove
        """
        if vehicle_id in self.vehicles:
            del self.vehicles[vehicle_id]
            
            # Update edge vehicle counts
            self._update_edge_vehicle_counts()
    
    def update(self, delta_time: float) -> None:
        """
        Update all vehicles.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        # Update vehicle positions
        for vehicle in list(self.vehicles.values()):
            vehicle.update_position(delta_time)
            
            # Remove vehicles that have arrived
            if vehicle.status == "arrived":
                self.remove_vehicle(vehicle.id)
        
        # Update edge vehicle counts
        self._update_edge_vehicle_counts()
    
    def _update_edge_vehicle_counts(self) -> None:
        """Update the count of vehicles on each edge"""
        # Reset counts
        for edge_id in self.edge_vehicle_counts:
            self.edge_vehicle_counts[edge_id] = 0
        
        # Count vehicles on each edge
        for vehicle in self.vehicles.values():
            if vehicle.status == "moving" and vehicle.route_progress < len(vehicle.current_route_edges):
                edge_id = vehicle.current_route_edges[vehicle.route_progress]['id']
                self.edge_vehicle_counts[edge_id] = self.edge_vehicle_counts.get(edge_id, 0) + 1
        
        # Update congestion levels in city graph
        for edge_id, count in self.edge_vehicle_counts.items():
            self.city_graph.update_edge_vehicle_count(edge_id, count)
    
    def reroute_vehicles(self, affected_edges: List[str]) -> None:
        """
        Reroute vehicles affected by incidents or congestion.
        
        Args:
            affected_edges: List of edge IDs affected
        """
        for vehicle in self.vehicles.values():
            # Check if vehicle is on an affected edge
            if vehicle.status == "moving" and vehicle.route_progress < len(vehicle.current_route_edges):
                current_edge_id = vehicle.current_route_edges[vehicle.route_progress]['id']
                
                # Check if current or upcoming edges are affected
                is_affected = current_edge_id in affected_edges
                
                if not is_affected:
                    # Check upcoming edges (up to 3)
                    for i in range(vehicle.route_progress + 1, min(vehicle.route_progress + 4, len(vehicle.current_route_edges))):
                        if vehicle.current_route_edges[i]['id'] in affected_edges:
                            is_affected = True
                            break
                
                if is_affected:
                    # Reroute the vehicle
                    vehicle.reroute(self.city_graph)
    
    def get_vehicles(self) -> List[Dict[str, Any]]:
        """Get all vehicles as dictionaries"""
        return [vehicle.to_dict() for vehicle in self.vehicles.values()]
    
    def get_edge_vehicle_counts(self) -> Dict[str, int]:
        """Get the count of vehicles on each edge"""
        return self.edge_vehicle_counts
    
    def a_star_routing(self, origin: Any, destination: Any) -> List[Any]:
        """
        Use A* algorithm for pathfinding.
        
        Args:
            origin: Origin node ID
            destination: Destination node ID
        
        Returns:
            List of node IDs forming the path
        """
        # Get node objects
        origin_node = self.city_graph.get_node_by_id(origin)
        destination_node = self.city_graph.get_node_by_id(destination)
        
        if not origin_node or not destination_node:
            return []
        
        # A* algorithm
        open_set = [(0, origin)]  # Priority queue of (f_score, node)
        came_from = {}  # Dictionary of node -> previous node
        
        # g_score is the cost from start to current node
        g_score = {origin: 0}
        
        # f_score is g_score + heuristic
        f_score = {origin: self._heuristic(origin_node, destination_node)}
        
        while open_set:
            # Get node with lowest f_score
            _, current = heapq.heappop(open_set)
            
            # Check if we've reached the destination
            if current == destination:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                
                # Reverse path (it's currently from destination to origin)
                path.reverse()
                return path
            
            # Explore neighbors
            for _, neighbor, k, data in self.city_graph.G.out_edges(current, keys=True, data=True):
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + data['travel_time']
                
                # If this path is better than any previous one
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Update path
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    # Calculate f_score
                    neighbor_node = self.city_graph.get_node_by_id(neighbor)
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor_node, destination_node)
                    
                    # Add to open set if not already there
                    for i, (_, node) in enumerate(open_set):
                        if node == neighbor:
                            open_set[i] = (f_score[neighbor], neighbor)
                            heapq.heapify(open_set)
                            break
                    else:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # No path found
        return []
    
    def _heuristic(self, node1: Dict[str, Any], node2: Dict[str, Any]) -> float:
        """
        Heuristic function for A* algorithm (Euclidean distance).
        
        Args:
            node1: First node
            node2: Second node
        
        Returns:
            Estimated cost between nodes
        """
        # Calculate Euclidean distance
        dx = node1['lon'] - node2['lon']
        dy = node1['lat'] - node2['lat']
        
        return (dx ** 2 + dy ** 2) ** 0.5
    
    def enhanced_routing(self, origin: Any, destination: Any) -> List[Any]:
        """Enhanced routing with better edge case handling"""
        try:
            # Multiple route options
            primary_route = self.a_star_routing(origin, destination)
            alternative_routes = self._calculate_alternative_routes(origin, destination)
            
            # Route evaluation
            best_route = self._evaluate_routes([primary_route] + alternative_routes)
            
            # Edge case handling
            if not best_route:
                return self._handle_routing_failure(origin, destination)
                
            # Emergency vehicle priority
            if self._is_emergency_vehicle():
                return self._calculate_emergency_route(best_route)
                
            return best_route
            
        except Exception as e:
            self._log_routing_error(e)
            return self._get_fallback_route(origin, destination)
