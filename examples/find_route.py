#!/usr/bin/env python3
"""Find the shortest route between two Algerian cities.

Usage:
    python find_route.py --from "Oran" --to "Constantine" --algorithm astar
    python find_route.py --from "Algiers" --to "Tamanrasset"
    python find_route.py --from "Tlemcen" --to "Annaba" --algorithm dijkstra --save route.html
"""

import argparse
import os
import sys

# Allow running from the examples/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cities import ALGERIAN_CITIES, list_cities
from src.graph_builder import GraphBuilder
from src.algorithms import PathFinder
from src.visualizer import RouteVisualizer


def main():
    parser = argparse.ArgumentParser(
        description="Find the shortest path between Algerian cities."
    )
    parser.add_argument(
        "--from", dest="source", required=True,
        help="Source city name (e.g. 'Oran')",
    )
    parser.add_argument(
        "--to", dest="target", required=True,
        help="Target city name (e.g. 'Constantine')",
    )
    parser.add_argument(
        "--algorithm", choices=["dijkstra", "astar", "bfs", "bellman_ford"],
        default="astar",
        help="Algorithm to use (default: astar)",
    )
    parser.add_argument(
        "--save", default=None,
        help="Save map to this HTML file path",
    )
    parser.add_argument(
        "--list-cities", action="store_true",
        help="List all available cities and exit",
    )

    args = parser.parse_args()

    if args.list_cities:
        print("Available cities:")
        for city in list_cities():
            lat, lon = ALGERIAN_CITIES[city]
            print(f"  {city:25s} ({lat:.4f}, {lon:.4f})")
        return

    if args.source not in ALGERIAN_CITIES:
        print(f"Error: Unknown source city '{args.source}'.")
        print(f"Available cities: {', '.join(list_cities())}")
        sys.exit(1)

    if args.target not in ALGERIAN_CITIES:
        print(f"Error: Unknown target city '{args.target}'.")
        print(f"Available cities: {', '.join(list_cities())}")
        sys.exit(1)

    # Build graph
    print("Building road network graph...")
    builder = GraphBuilder()
    graph = builder.build_synthetic(ALGERIAN_CITIES)
    stats = builder.get_stats()
    print(f"Graph: {stats['node_count']} cities, {stats['edge_count']} road connections")
    print()

    # Find path
    finder = PathFinder(graph)
    algo_func = {
        "dijkstra": finder.dijkstra,
        "astar": finder.astar,
        "bfs": finder.bfs,
        "bellman_ford": finder.bellman_ford,
    }

    print(f"Finding shortest path: {args.source} -> {args.target}")
    print(f"Algorithm: {args.algorithm}")
    print()

    result = algo_func[args.algorithm](args.source, args.target)

    if not result.found:
        print("No path found between these cities!")
        sys.exit(1)

    print(result.summary())
    print()
    print("Route:")
    for i, city in enumerate(result.path):
        prefix = "  Start -> " if i == 0 else "       -> " if i < len(result.path) - 1 else "   End -> "
        print(f"{prefix}{city}")

    # Save map
    output_path = args.save or "results/route_map.html"
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    print(f"\nGenerating map...")
    viz = RouteVisualizer()
    viz.add_cities(ALGERIAN_CITIES)
    viz.add_graph_edges(graph, ALGERIAN_CITIES)
    viz.add_route(
        path=result.path,
        coords_dict=ALGERIAN_CITIES,
        color="#2196F3",
        label=f"{result.algorithm}: {result.distance_km:.1f} km",
    )
    viz.save(output_path)
    print(f"Map saved to: {output_path}")


if __name__ == "__main__":
    main()
