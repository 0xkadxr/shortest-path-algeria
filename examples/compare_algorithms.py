#!/usr/bin/env python3
"""Compare all shortest path algorithms between two Algerian cities.

Usage:
    python compare_algorithms.py --from "Oran" --to "Algiers"
    python compare_algorithms.py --from "Constantine" --to "Ghardaia" --save comparison.html
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cities import ALGERIAN_CITIES, list_cities
from src.graph_builder import GraphBuilder
from src.algorithms import PathFinder, format_comparison_table
from src.visualizer import RouteVisualizer


def main():
    parser = argparse.ArgumentParser(
        description="Compare shortest path algorithms between Algerian cities."
    )
    parser.add_argument(
        "--from", dest="source", required=True,
        help="Source city name",
    )
    parser.add_argument(
        "--to", dest="target", required=True,
        help="Target city name",
    )
    parser.add_argument(
        "--save", default=None,
        help="Save comparison map to this HTML file path",
    )

    args = parser.parse_args()

    if args.source not in ALGERIAN_CITIES:
        print(f"Error: Unknown city '{args.source}'.")
        print(f"Available: {', '.join(list_cities())}")
        sys.exit(1)

    if args.target not in ALGERIAN_CITIES:
        print(f"Error: Unknown city '{args.target}'.")
        print(f"Available: {', '.join(list_cities())}")
        sys.exit(1)

    # Build graph
    print("Building road network graph...")
    builder = GraphBuilder()
    graph = builder.build_synthetic(ALGERIAN_CITIES)
    stats = builder.get_stats()
    print(f"Graph: {stats['node_count']} cities, {stats['edge_count']} connections")
    print()

    # Run all algorithms
    print(f"Comparing algorithms: {args.source} -> {args.target}")
    print()

    finder = PathFinder(graph)
    results = finder.compare_all(args.source, args.target)

    # Print comparison table
    print(format_comparison_table(results))
    print()

    # Print individual paths
    for algo_name, result in results.items():
        if result.found:
            route_str = " -> ".join(str(c) for c in result.path)
            print(f"{algo_name}: {route_str}")
        else:
            print(f"{algo_name}: No path found")
    print()

    # Generate map
    output_path = args.save or "results/comparison_map.html"
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    print("Generating comparison map...")
    viz = RouteVisualizer()
    viz.add_cities(ALGERIAN_CITIES)
    viz.add_graph_edges(graph, ALGERIAN_CITIES)
    viz.add_multiple_routes(results, ALGERIAN_CITIES)
    viz.add_comparison_legend(results)
    viz.save(output_path)
    print(f"Map saved to: {output_path}")


if __name__ == "__main__":
    main()
