"""Shortest path algorithms implemented from scratch.

Includes Dijkstra, A*, BFS, and Bellman-Ford. Each algorithm is implemented
manually using basic data structures rather than delegating to NetworkX.
"""

import heapq
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class PathResult:
    """Result of a shortest path computation."""

    algorithm: str
    path: list = field(default_factory=list)
    distance_km: float = float("inf")
    nodes_explored: int = 0
    execution_time_ms: float = 0.0

    @property
    def found(self) -> bool:
        """Whether a path was found."""
        return len(self.path) > 0

    def summary(self) -> str:
        """Return a human-readable summary."""
        if not self.found:
            return f"[{self.algorithm}] No path found."
        return (
            f"[{self.algorithm}] Distance: {self.distance_km:.2f} km | "
            f"Nodes explored: {self.nodes_explored} | "
            f"Time: {self.execution_time_ms:.3f} ms | "
            f"Path: {' -> '.join(str(n) for n in self.path)}"
        )


class PathFinder:
    """Find shortest paths on a weighted graph using various algorithms.

    The graph must be a NetworkX Graph with ``weight`` attributes on edges
    and ``y`` (latitude) / ``x`` (longitude) attributes on nodes (needed
    for heuristic-based algorithms).

    Args:
        graph: A ``networkx.Graph`` instance.
    """

    def __init__(self, graph):
        self.graph = graph

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _neighbors(self, node):
        """Yield (neighbor, weight) tuples for *node*."""
        for neighbor in self.graph.neighbors(node):
            weight = self.graph[node][neighbor].get("weight", 1.0)
            yield neighbor, weight

    def _reconstruct(self, predecessors, source, target):
        """Trace back the path from *target* to *source*."""
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        path.reverse()
        if path and path[0] == source:
            return path
        return []

    def _node_coord(self, node):
        """Return (lat, lon) for a node."""
        data = self.graph.nodes[node]
        return (data["y"], data["x"])

    # ------------------------------------------------------------------
    # Dijkstra's algorithm
    # ------------------------------------------------------------------

    def dijkstra(self, source, target) -> PathResult:
        """Dijkstra's shortest path algorithm.

        Uses a min-heap priority queue for efficient extraction of the
        closest unvisited node.

        Args:
            source: Start node.
            target: Goal node.

        Returns:
            A :class:`PathResult` with the shortest path and metrics.
        """
        start_time = time.perf_counter()

        dist = {source: 0.0}
        predecessors = {source: None}
        visited = set()
        nodes_explored = 0

        # Priority queue entries: (distance, tiebreaker, node)
        counter = 0
        pq = [(0.0, counter, source)]

        while pq:
            current_dist, _, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)
            nodes_explored += 1

            if current == target:
                break

            for neighbor, weight in self._neighbors(current):
                if neighbor in visited:
                    continue
                new_dist = current_dist + weight
                if new_dist < dist.get(neighbor, float("inf")):
                    dist[neighbor] = new_dist
                    predecessors[neighbor] = current
                    counter += 1
                    heapq.heappush(pq, (new_dist, counter, neighbor))

        elapsed = (time.perf_counter() - start_time) * 1000.0
        path = self._reconstruct(predecessors, source, target)

        return PathResult(
            algorithm="Dijkstra",
            path=path,
            distance_km=round(dist.get(target, float("inf")), 2),
            nodes_explored=nodes_explored,
            execution_time_ms=round(elapsed, 3),
        )

    # ------------------------------------------------------------------
    # A* search
    # ------------------------------------------------------------------

    def astar(self, source, target, heuristic="haversine") -> PathResult:
        """A* search with a configurable heuristic.

        Args:
            source: Start node.
            target: Goal node.
            heuristic: Heuristic name ('haversine', 'euclidean',
                'manhattan', 'zero') or a callable(coord1, coord2)->float.

        Returns:
            A :class:`PathResult` with the shortest path and metrics.
        """
        # Resolve heuristic
        if callable(heuristic):
            h_func = heuristic
        else:
            from .heuristics import get_heuristic
            h_func = get_heuristic(heuristic)

        target_coord = self._node_coord(target)

        start_time = time.perf_counter()

        g_score = {source: 0.0}
        f_score = {source: h_func(self._node_coord(source), target_coord)}
        predecessors = {source: None}
        visited = set()
        nodes_explored = 0

        counter = 0
        open_set = [(f_score[source], counter, source)]

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)
            nodes_explored += 1

            if current == target:
                break

            for neighbor, weight in self._neighbors(current):
                if neighbor in visited:
                    continue

                tentative_g = g_score[current] + weight

                if tentative_g < g_score.get(neighbor, float("inf")):
                    g_score[neighbor] = tentative_g
                    h = h_func(self._node_coord(neighbor), target_coord)
                    f_score[neighbor] = tentative_g + h
                    predecessors[neighbor] = current
                    counter += 1
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))

        elapsed = (time.perf_counter() - start_time) * 1000.0
        path = self._reconstruct(predecessors, source, target)

        return PathResult(
            algorithm="A*",
            path=path,
            distance_km=round(g_score.get(target, float("inf")), 2),
            nodes_explored=nodes_explored,
            execution_time_ms=round(elapsed, 3),
        )

    # ------------------------------------------------------------------
    # Breadth-First Search (unweighted)
    # ------------------------------------------------------------------

    def bfs(self, source, target) -> PathResult:
        """Breadth-First Search (unweighted shortest path).

        Finds the path with the fewest hops. Edge weights are ignored;
        the ``distance_km`` in the result is the sum of weights along
        the path found, but it is **not** guaranteed to be minimal in
        terms of total weight.

        Args:
            source: Start node.
            target: Goal node.

        Returns:
            A :class:`PathResult` with the path and metrics.
        """
        start_time = time.perf_counter()

        visited = {source}
        predecessors = {source: None}
        queue = deque([source])
        nodes_explored = 0

        found = False
        while queue:
            current = queue.popleft()
            nodes_explored += 1

            if current == target:
                found = True
                break

            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    predecessors[neighbor] = current
                    queue.append(neighbor)

        elapsed = (time.perf_counter() - start_time) * 1000.0
        path = self._reconstruct(predecessors, source, target) if found else []

        # Compute actual weighted distance along the BFS path
        distance = 0.0
        if path:
            for i in range(len(path) - 1):
                distance += self.graph[path[i]][path[i + 1]].get("weight", 1.0)

        return PathResult(
            algorithm="BFS",
            path=path,
            distance_km=round(distance, 2),
            nodes_explored=nodes_explored,
            execution_time_ms=round(elapsed, 3),
        )

    # ------------------------------------------------------------------
    # Bellman-Ford
    # ------------------------------------------------------------------

    def bellman_ford(self, source, target) -> PathResult:
        """Bellman-Ford shortest path algorithm.

        Can handle negative edge weights and detects negative-weight
        cycles. Runs in O(V * E) time.

        Args:
            source: Start node.
            target: Goal node.

        Returns:
            A :class:`PathResult` with the shortest path and metrics.

        Raises:
            ValueError: If a negative-weight cycle is detected.
        """
        start_time = time.perf_counter()

        nodes = list(self.graph.nodes)
        edges = []
        for u, v, data in self.graph.edges(data=True):
            w = data.get("weight", 1.0)
            edges.append((u, v, w))
            edges.append((v, u, w))  # undirected

        dist = {node: float("inf") for node in nodes}
        dist[source] = 0.0
        predecessors = {node: None for node in nodes}
        nodes_explored = 0

        n = len(nodes)
        for i in range(n - 1):
            updated = False
            for u, v, w in edges:
                nodes_explored += 1
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    predecessors[v] = u
                    updated = True
            if not updated:
                break  # Early termination - no updates means we're done

        # Check for negative cycles
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                raise ValueError(
                    "Graph contains a negative-weight cycle reachable from "
                    f"source '{source}'."
                )

        elapsed = (time.perf_counter() - start_time) * 1000.0
        path = self._reconstruct(predecessors, source, target)

        return PathResult(
            algorithm="Bellman-Ford",
            path=path,
            distance_km=round(dist.get(target, float("inf")), 2),
            nodes_explored=nodes_explored,
            execution_time_ms=round(elapsed, 3),
        )

    # ------------------------------------------------------------------
    # Compare all algorithms
    # ------------------------------------------------------------------

    def compare_all(self, source, target) -> dict:
        """Run all algorithms on the same source-target pair and compare.

        Args:
            source: Start node.
            target: Goal node.

        Returns:
            Dict mapping algorithm name to its :class:`PathResult`.
        """
        results = {}
        results["Dijkstra"] = self.dijkstra(source, target)
        results["A*"] = self.astar(source, target)
        results["BFS"] = self.bfs(source, target)
        results["Bellman-Ford"] = self.bellman_ford(source, target)
        return results


def format_comparison_table(results: dict) -> str:
    """Format comparison results as a readable text table.

    Args:
        results: Dict of algorithm_name -> PathResult.

    Returns:
        A formatted string table.
    """
    header = (
        f"{'Algorithm':<15} {'Distance (km)':>14} {'Nodes Explored':>15} "
        f"{'Time (ms)':>10} {'Path Length':>12}"
    )
    sep = "-" * len(header)
    lines = [sep, header, sep]

    for name, result in results.items():
        path_len = len(result.path) if result.found else 0
        dist_str = f"{result.distance_km:.2f}" if result.found else "N/A"
        lines.append(
            f"{name:<15} {dist_str:>14} {result.nodes_explored:>15} "
            f"{result.execution_time_ms:>10.3f} {path_len:>12}"
        )

    lines.append(sep)
    return "\n".join(lines)
