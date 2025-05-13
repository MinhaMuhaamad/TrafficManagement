import osmnx as ox
import networkx as nx
import numpy as np
import random
from typing import Dict, List, Tuple, Any, Optional
import json

class CityGraph:
    def __init__(self, city_name: str, use_cache: bool = True):
        """
        Initialize a city graph using OpenStreetMap data.
        
        Args:
            city_name: Name of the city to model
            use_cache: Whether to use cached data if available
        """
        self.city_name = city_name
        self.use_cache = use_cache
        
        # Try to load from cache first
        self.G = self._load_graph()
        
        # If not in cache or cache not used, download from OSM
        if self.G is None:
            print(f"Downloading OSM data for {city_name}...")
            try:
                # Get the graph from OSM
                self.G = ox.graph_from_place(city_name, network_type='drive')
                
                # Simplify the graph
                self.G = ox.simplify_graph(self.G)
                
                # Project the graph to use meters
                self.G = ox.project_graph(self.G)
                
                # Add edge speeds and travel times
                self.G = ox.add_edge_speeds(self.G)
                self.G = ox.add_edge_travel_times(self.G)
                
                # Save to cache
                self._save_graph()
                
            except Exception as e:
                print(f"Error downloading OSM data: {e}")
                # Create a simple grid graph as fallback
                self.G = self._create_grid_graph()
        
        # Add additional attributes to edges
        self._add_edge_attributes()
        
        # Create a mapping of node IDs to indices for easier access
        self.node_to_idx = {node: i for i, node in enumerate(self.G.nodes())}
        self.idx_to_node = {i: node for node, i in self.node_to_idx.items()}
        
        # Extract nodes and edges for easier access
        self.nodes = self._extract_nodes()
        self.edges = self._extract_edges()
        
        print(f"City graph created with {len(self.nodes)} nodes and {len(self.edges)} edges")
    
    def _load_graph(self) -> Optional[nx.MultiDiGraph]:
        """Load graph from cache if available"""
        if not self.use_cache:
            return None
        
        try:
            # Replace spaces with underscores for filename
            filename = f"cache/{self.city_name.replace(' ', '_').lower()}.graphml"
            return ox.load_graphml(filename)
        except:
            return None
    
    def _save_graph(self) -> None:
        """Save graph to cache"""
        try:
            # Replace spaces with underscores for filename
            filename = f"cache/{self.city_name.replace(' ', '_').lower()}.graphml"
            ox.save_graphml(self.G, filename)
        except Exception as e:
            print(f"Error saving graph to cache: {e}")
    
    def _create_grid_graph(self) -> nx.MultiDiGraph:
        """Create a simple grid graph as fallback"""
        print("Creating fallback grid graph...")
        
        # Create a 10x10 grid graph
        G = nx.grid_graph(dim=[10, 10])
        
        # Convert to directed graph
        G = nx.DiGraph(G)
        
        # Add some random coordinates centered around the city
        if self.city_name == "San Francisco":
            center = (37.7749, -122.4194)
        elif self.city_name == "New York":
            center = (40.7128, -74.0060)
        elif self.city_name == "Chicago":
            center = (41.8781, -87.6298)
        elif self.city_name == "Boston":
            center = (42.3601, -71.0589)
        elif self.city_name == "Seattle":
            center = (47.6062, -122.3321)
        else:
            center = (0, 0)
        
        # Add coordinates to nodes
        for node in G.nodes():
            x, y = node
            # Scale to be around 0.01 degrees apart (roughly 1km)
            lat = center[0] + (y - 5) * 0.01
            lon = center[1] + (x - 5) * 0.01
            G.nodes[node]['x'] = lon
            G.nodes[node]['y'] = lat
            G.nodes[node]['lon'] = lon
            G.nodes[node]['lat'] = lat
        
        # Convert to MultiDiGraph to match OSMnx format
        G = nx.MultiDiGraph(G)
        
        return G
    
    def _add_edge_attributes(self) -> None:
        """Add additional attributes to edges"""
        for u, v, k, data in self.G.edges(keys=True, data=True):
            # Add unique ID to each edge
            self.G[u][v][k]['id'] = f"{u}_{v}_{k}"
            
            # Add congestion level (0 to 1)
            self.G[u][v][k]['congestion'] = 0.0
            
            # Add current vehicle count
            self.G[u][v][k]['vehicle_count'] = 0
            
            # Add capacity (vehicles per unit time)
            # If the edge has a 'lanes' attribute, use it, otherwise assume 1
            lanes = data.get('lanes', 1)
            if isinstance(lanes, list):
                lanes = lanes[0]
            try:
                lanes = int(lanes)
            except:
                lanes = 1
            
            # Capacity is proportional to number of lanes
            self.G[u][v][k]['capacity'] = lanes * 10
            
            # If edge doesn't have travel_time, add it
            if 'travel_time' not in data:
                # Get length in meters
                length = data.get('length', 100)
                
                # Assume 30 km/h if speed not available
                speed = data.get('speed_kph', 30)
                
                # Calculate travel time in seconds
                travel_time = (length / 1000) / (speed / 3600)
                self.G[u][v][k]['travel_time'] = travel_time
    
    def _extract_nodes(self) -> List[Dict[str, Any]]:
        """Extract nodes with their attributes"""
        nodes = []
        for node, data in self.G.nodes(data=True):
            # Get coordinates
            lat = data.get('y', data.get('lat', 0))
            lon = data.get('x', data.get('lon', 0))
            
            nodes.append({
                'id': node,
                'lat': lat,
                'lon': lon,
                'is_intersection': self.G.out_degree(node) > 1
            })
        
        return nodes
    
    def _extract_edges(self) -> List[Dict[str, Any]]:
        """Extract edges with their attributes"""
        edges = []
        for u, v, k, data in self.G.edges(keys=True, data=True):
            # Get source and target node data
            source_data = self.G.nodes[u]
            target_data = self.G.nodes[v]
            
            # Get coordinates
            source_lat = source_data.get('y', source_data.get('lat', 0))
            source_lon = source_data.get('x', source_data.get('lon', 0))
            target_lat = target_data.get('y', target_data.get('lat', 0))
            target_lon = target_data.get('x', target_data.get('lon', 0))
            
            edges.append({
                'id': data['id'],
                'source': u,
                'target': v,
                'key': k,
                'source_lat': source_lat,
                'source_lon': source_lon,
                'target_lat': target_lat,
                'target_lon': target_lon,
                'length': data.get('length', 100),
                'travel_time': data.get('travel_time', 60),
                'congestion': data.get('congestion', 0.0),
                'vehicle_count': data.get('vehicle_count', 0),
                'capacity': data.get('capacity', 10),
                'name': data.get('name', f"Road {u} to {v}")
            })
        
        return edges
    
    def get_node_by_id(self, node_id: Any) -> Dict[str, Any]:
        """Get node by ID"""
        for node in self.nodes:
            if node['id'] == node_id:
                return node
        return None
    
    def get_edge_by_id(self, edge_id: str) -> Dict[str, Any]:
        """Get edge by ID"""
        for edge in self.edges:
            if edge['id'] == edge_id:
                return edge
        return None
    
    def get_nearest_node(self, lat: float, lon: float) -> Any:
        """Get the nearest node to a given point"""
        # Simple Euclidean distance for now
        min_dist = float('inf')
        nearest_node = None
        
        for node in self.nodes:
            dist = (node['lat'] - lat) ** 2 + (node['lon'] - lon) ** 2
            if dist < min_dist:  # Fixed: Changed &lt; to <
                min_dist = dist
                nearest_node = node['id']
        
        return nearest_node
    
    def get_shortest_path(self, source: Any, target: Any) -> List[Any]:
        """Get the shortest path between two nodes using Dijkstra's algorithm"""
        try:
            return nx.shortest_path(self.G, source, target, weight='travel_time')
        except nx.NetworkXNoPath:
            return []
    
    def get_path_with_nodes(self, path: List[Any]) -> List[Dict[str, Any]]:
        """Convert a path of node IDs to a list of node objects"""
        return [self.get_node_by_id(node_id) for node_id in path]
    
    def update_edge_congestion(self, edge_id: str, congestion: float) -> None:
        """Update the congestion level of an edge"""
        for u, v, k, data in self.G.edges(keys=True, data=True):
            if data['id'] == edge_id:
                self.G[u][v][k]['congestion'] = max(0, min(1, congestion))
                
                # Update travel time based on congestion
                base_travel_time = data.get('base_travel_time', data['travel_time'])
                
                # Save the original travel time if not already saved
                if 'base_travel_time' not in data:
                    self.G[u][v][k]['base_travel_time'] = data['travel_time']
                
                # Increase travel time based on congestion (up to 5x when fully congested)
                congestion_factor = 1 + 4 * congestion
                self.G[u][v][k]['travel_time'] = base_travel_time * congestion_factor
                
                # Update the edge in our list
                for edge in self.edges:
                    if edge['id'] == edge_id:
                        edge['congestion'] = congestion
                        break
