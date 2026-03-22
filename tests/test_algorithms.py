"""Tests for shortest path algorithms and supporting modules."""

import math
import pytest
import networkx as nx

from src.algorithms import PathFinder, PathResult
from src.heuristics import haversine, euclidean, manhattan, zero_heuristic
from src.graph_builder import GraphBuilder
from src.cities import ALGERIAN_CITIES, get_city_coords, list_cities


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_graph():
    """A small weighted graph with a known shortest path.

    Graph layout:
        A --1-- B --2-- C
        |               |
        4               1
        |               |
        D ------3------ E

    Shortest A->E: A-B-C-E  (1+2+1 = 4)
    """
    G = nx.Graph()
    G.add_node("A", y=0.0, x=0.0)
    G.add_node("B", y=0.0, x=1.0)
    G.add_node("C", y=0.0, x=2.0)
    G.add_node("D", y=1.0, x=0.0)
    G.add_node("E", y=1.0, x=2.0)

    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "C", weight=2.0)
    G.add_edge("A", "D", weight=4.0)
    G.add_edge("D", "E", weight=3.0)
    G.add_edge("C", "E", weight=1.0)

    return G


@pytest.fixture
def algeria_graph():
    """A synthetic graph of Algerian cities."""
    builder = GraphBuilder()
    builder.build_synthetic(ALGERIAN_CITIES)
    return builder.get_graph()


# ---------------------------------------------------------------------------
# Haversine tests
# ---------------------------------------------------------------------------

class TestHaversine:
    def test_same_point(self):
        assert haversine((36.0, 3.0), (36.0, 3.0)) == 0.0

    def test_algiers_to_oran(self):
        """Algiers to Oran is roughly 350-370 km straight line."""
        dist = haversine(
            ALGERIAN_CITIES["Algiers"],
            ALGERIAN_CITIES["Oran"],
        )
        assert 300 < dist < 420

    def test_known_distance(self):
        """New York (40.7128, -74.0060) to London (51.5074, -0.1278)
        is approximately 5,570 km."""
        dist = haversine((40.7128, -74.0060), (51.5074, -0.1278))
        assert 5500 < dist < 5650

    def test_symmetry(self):
        c1 = (36.7538, 3.0588)
        c2 = (35.6969, -0.6331)
        assert abs(haversine(c1, c2) - haversine(c2, c1)) < 1e-10

    def test_antipodal_points(self):
        """Points on opposite sides of the Earth should be ~20,000 km."""
        dist = haversine((0.0, 0.0), (0.0, 180.0))
        assert 20000 < dist < 20100


class TestOtherHeuristics:
    def test_euclidean_zero(self):
        assert euclidean((0.0, 0.0), (0.0, 0.0)) == 0.0

    def test_manhattan_zero(self):
        assert manhattan((0.0, 0.0), (0.0, 0.0)) == 0.0

    def test_zero_heuristic(self):
        assert zero_heuristic((10.0, 20.0), (30.0, 40.0)) == 0.0

    def test_euclidean_less_than_manhattan(self):
        c1 = (36.0, 3.0)
        c2 = (37.0, 4.0)
        assert euclidean(c1, c2) <= manhattan(c1, c2)


# ---------------------------------------------------------------------------
# Algorithm correctness on simple graph
# ---------------------------------------------------------------------------

class TestAlgorithmsSimpleGraph:
    def test_dijkstra_shortest_path(self, simple_graph):
        finder = PathFinder(simple_graph)
        result = finder.dijkstra("A", "E")
        assert result.found
        assert result.path == ["A", "B", "C", "E"]
        assert result.distance_km == pytest.approx(4.0)

    def test_astar_shortest_path(self, simple_graph):
        finder = PathFinder(simple_graph)
        result = finder.astar("A", "E", heuristic="zero")
        assert result.found
        assert result.path == ["A", "B", "C", "E"]
        assert result.distance_km == pytest.approx(4.0)

    def test_bfs_finds_path(self, simple_graph):
        finder = PathFinder(simple_graph)
        result = finder.bfs("A", "E")
        assert result.found
        # BFS finds shortest hop-count path, which may differ
        assert result.path[0] == "A"
        assert result.path[-1] == "E"

    def test_bellman_ford_shortest_path(self, simple_graph):
        finder = PathFinder(simple_graph)
        result = finder.bellman_ford("A", "E")
        assert result.found
        assert result.path == ["A", "B", "C", "E"]
        assert result.distance_km == pytest.approx(4.0)

    def test_no_path(self):
        G = nx.Graph()
        G.add_node("A", y=0.0, x=0.0)
        G.add_node("B", y=1.0, x=1.0)
        # No edge between A and B
        finder = PathFinder(G)
        result = finder.dijkstra("A", "B")
        assert not result.found

    def test_same_source_target(self, simple_graph):
        finder = PathFinder(simple_graph)
        result = finder.dijkstra("A", "A")
        assert result.found
        assert result.path == ["A"]
        assert result.distance_km == 0.0

    def test_all_optimal_agree(self, simple_graph):
        """Dijkstra, A*, and Bellman-Ford should all find the same
        optimal distance on positive-weight graphs."""
        finder = PathFinder(simple_graph)
        d = finder.dijkstra("A", "E")
        a = finder.astar("A", "E", heuristic="zero")
        bf = finder.bellman_ford("A", "E")

        assert d.distance_km == pytest.approx(a.distance_km)
        assert d.distance_km == pytest.approx(bf.distance_km)

    def test_compare_all(self, simple_graph):
        finder = PathFinder(simple_graph)
        results = finder.compare_all("A", "E")
        assert len(results) == 4
        for name, result in results.items():
            assert result.found


# ---------------------------------------------------------------------------
# Algorithm tests on Algeria graph
# ---------------------------------------------------------------------------

class TestAlgorithmsAlgeria:
    def test_dijkstra_algiers_oran(self, algeria_graph):
        finder = PathFinder(algeria_graph)
        result = finder.dijkstra("Algiers", "Oran")
        assert result.found
        assert result.path[0] == "Algiers"
        assert result.path[-1] == "Oran"
        assert result.distance_km > 0

    def test_astar_algiers_constantine(self, algeria_graph):
        finder = PathFinder(algeria_graph)
        result = finder.astar("Algiers", "Constantine")
        assert result.found
        assert result.distance_km > 0

    def test_algorithms_same_optimal(self, algeria_graph):
        finder = PathFinder(algeria_graph)
        d = finder.dijkstra("Oran", "Constantine")
        a = finder.astar("Oran", "Constantine")
        bf = finder.bellman_ford("Oran", "Constantine")

        assert d.distance_km == pytest.approx(a.distance_km, rel=1e-6)
        assert d.distance_km == pytest.approx(bf.distance_km, rel=1e-6)

    def test_path_result_dataclass(self, algeria_graph):
        finder = PathFinder(algeria_graph)
        result = finder.dijkstra("Algiers", "Oran")
        assert isinstance(result, PathResult)
        assert result.algorithm == "Dijkstra"
        assert result.nodes_explored > 0
        assert result.execution_time_ms >= 0


# ---------------------------------------------------------------------------
# Graph builder tests
# ---------------------------------------------------------------------------

class TestGraphBuilder:
    def test_build_from_cities(self):
        builder = GraphBuilder()
        graph = builder.build_from_cities(ALGERIAN_CITIES, max_distance_km=300)
        stats = builder.get_stats()
        assert stats["node_count"] == len(ALGERIAN_CITIES)
        assert stats["edge_count"] > 0

    def test_build_synthetic_connected(self):
        builder = GraphBuilder()
        graph = builder.build_synthetic(ALGERIAN_CITIES)
        stats = builder.get_stats()
        assert stats["is_connected"]

    def test_small_graph(self):
        cities = {
            "A": (36.0, 3.0),
            "B": (36.5, 3.5),
            "C": (37.0, 4.0),
        }
        builder = GraphBuilder()
        graph = builder.build_from_cities(cities, max_distance_km=200)
        assert graph.number_of_nodes() == 3

    def test_stats_empty_graph(self):
        builder = GraphBuilder()
        stats = builder.get_stats()
        assert stats["node_count"] == 0


# ---------------------------------------------------------------------------
# Cities module tests
# ---------------------------------------------------------------------------

class TestCities:
    def test_get_city_coords(self):
        lat, lon = get_city_coords("Algiers")
        assert lat == pytest.approx(36.7538)
        assert lon == pytest.approx(3.0588)

    def test_unknown_city_raises(self):
        with pytest.raises(KeyError):
            get_city_coords("Atlantis")

    def test_list_cities(self):
        cities = list_cities()
        assert len(cities) >= 20
        assert "Algiers" in cities
        assert cities == sorted(cities)  # should be sorted

    def test_city_count(self):
        assert len(ALGERIAN_CITIES) >= 20
