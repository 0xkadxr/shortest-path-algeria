"""Build road network graphs from OpenStreetMap data or synthetic city data."""

import itertools
import networkx as nx

from .heuristics import haversine
from .cities import ALGERIAN_CITIES


# Factor to convert straight-line distance to estimated road distance.
# Roads are typically 1.3-1.5 times the straight-line distance.
_ROAD_FACTOR = 1.35


class GraphBuilder:
    """Build and manage road network graphs for Algerian cities."""

    def __init__(self):
        self._graph = nx.Graph()
        self._city_coords = {}

    def build_from_osm(self, place_name: str = "Algeria",
                       network_type: str = "drive") -> nx.Graph:
        """Download and build a road network graph from OpenStreetMap.

        Requires the ``osmnx`` package to be installed.

        Args:
            place_name: Place name to query (e.g. 'Algeria', 'Algiers, Algeria').
            network_type: OSM network type ('drive', 'walk', 'bike', 'all').

        Returns:
            A NetworkX graph of the road network.
        """
        try:
            import osmnx as ox
        except ImportError:
            raise ImportError(
                "osmnx is required for OSM data. "
                "Install it with: pip install osmnx"
            )

        G = ox.graph_from_place(place_name, network_type=network_type)
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)

        self._graph = nx.Graph()
        for u, v, data in G.edges(data=True):
            length_km = data.get("length", 0) / 1000.0
            self._graph.add_edge(u, v, weight=length_km)

        for node, data in G.nodes(data=True):
            self._graph.nodes[node]["y"] = data.get("y", 0)
            self._graph.nodes[node]["x"] = data.get("x", 0)

        return self._graph

    def build_from_cities(self, cities_dict: dict = None,
                          max_distance_km: float = 300.0) -> nx.Graph:
        """Build a graph connecting cities within a maximum distance.

        Args:
            cities_dict: Dict of city_name -> (lat, lon). Defaults to
                ALGERIAN_CITIES.
            max_distance_km: Maximum straight-line distance (km) to create
                an edge between two cities.

        Returns:
            A NetworkX graph of connected cities.
        """
        if cities_dict is None:
            cities_dict = ALGERIAN_CITIES

        self._graph = nx.Graph()
        self._city_coords = dict(cities_dict)

        # Add nodes
        for city, (lat, lon) in cities_dict.items():
            self._graph.add_node(city, y=lat, x=lon)

        # Add edges for cities within max_distance_km
        for city_a, city_b in itertools.combinations(cities_dict.keys(), 2):
            coord_a = cities_dict[city_a]
            coord_b = cities_dict[city_b]
            dist = haversine(coord_a, coord_b)
            if dist <= max_distance_km:
                road_dist = dist * _ROAD_FACTOR
                self._graph.add_edge(city_a, city_b, weight=round(road_dist, 2))

        return self._graph

    def build_synthetic(self, cities_dict: dict = None) -> nx.Graph:
        """Build a synthetic road network based on geographical proximity.

        Creates edges between cities using Haversine distance multiplied
        by a road factor to estimate real road distances. Nearby cities
        get edges; distant cities connect only through intermediate hops.

        Uses adaptive distance thresholds to ensure a connected graph:
        - Direct neighbours: cities within 200 km
        - Regional connections: cities within 400 km (added if needed for
          connectivity)

        Args:
            cities_dict: Dict of city_name -> (lat, lon). Defaults to
                ALGERIAN_CITIES.

        Returns:
            A NetworkX graph of the synthetic road network.
        """
        if cities_dict is None:
            cities_dict = ALGERIAN_CITIES

        self._graph = nx.Graph()
        self._city_coords = dict(cities_dict)

        # Add all city nodes
        for city, (lat, lon) in cities_dict.items():
            self._graph.add_node(city, y=lat, x=lon)

        # Compute all pairwise distances
        all_distances = []
        for city_a, city_b in itertools.combinations(cities_dict.keys(), 2):
            dist = haversine(cities_dict[city_a], cities_dict[city_b])
            all_distances.append((dist, city_a, city_b))

        all_distances.sort()

        # Phase 1: add edges for nearby cities (< 200 km)
        for dist, city_a, city_b in all_distances:
            if dist <= 200.0:
                road_dist = dist * _ROAD_FACTOR
                self._graph.add_edge(city_a, city_b, weight=round(road_dist, 2))

        # Phase 2: ensure connectivity by adding longer edges if needed
        if not nx.is_connected(self._graph):
            for dist, city_a, city_b in all_distances:
                if dist <= 400.0 and not nx.has_path(self._graph, city_a, city_b):
                    road_dist = dist * _ROAD_FACTOR
                    self._graph.add_edge(city_a, city_b, weight=round(road_dist, 2))
                if nx.is_connected(self._graph):
                    break

        # Phase 3: last resort - connect all components via nearest pair
        if not nx.is_connected(self._graph):
            components = list(nx.connected_components(self._graph))
            while len(components) > 1:
                best_dist = float("inf")
                best_pair = None
                for i, comp_a in enumerate(components):
                    for comp_b in components[i + 1:]:
                        for ca in comp_a:
                            for cb in comp_b:
                                d = haversine(cities_dict[ca], cities_dict[cb])
                                if d < best_dist:
                                    best_dist = d
                                    best_pair = (ca, cb)
                if best_pair:
                    road_dist = best_dist * _ROAD_FACTOR
                    self._graph.add_edge(
                        best_pair[0], best_pair[1],
                        weight=round(road_dist, 2),
                    )
                components = list(nx.connected_components(self._graph))

        return self._graph

    def get_graph(self) -> nx.Graph:
        """Return the current graph."""
        return self._graph

    def get_stats(self) -> dict:
        """Return statistics about the current graph.

        Returns:
            Dict with keys: node_count, edge_count, connected_components,
            is_connected, avg_degree.
        """
        if len(self._graph) == 0:
            return {
                "node_count": 0,
                "edge_count": 0,
                "connected_components": 0,
                "is_connected": False,
                "avg_degree": 0.0,
            }

        degrees = [d for _, d in self._graph.degree()]
        return {
            "node_count": self._graph.number_of_nodes(),
            "edge_count": self._graph.number_of_edges(),
            "connected_components": nx.number_connected_components(self._graph),
            "is_connected": nx.is_connected(self._graph),
            "avg_degree": round(sum(degrees) / len(degrees), 2),
        }
