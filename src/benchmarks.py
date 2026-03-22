"""Benchmark and compare shortest path algorithm performance."""

import itertools
import time
from dataclasses import dataclass, field

from .algorithms import PathFinder, format_comparison_table


@dataclass
class BenchmarkEntry:
    """A single benchmark measurement."""

    source: str
    target: str
    algorithm: str
    distance_km: float
    nodes_explored: int
    execution_time_ms: float
    path_length: int
    found: bool


class AlgorithmBenchmark:
    """Run benchmarks across multiple city pairs and algorithms.

    Args:
        graph: A NetworkX graph.
    """

    def __init__(self, graph):
        self.graph = graph
        self.finder = PathFinder(graph)
        self.results: list[BenchmarkEntry] = []

    def run_benchmark(self, city_pairs: list[tuple],
                      algorithms: list[str] = None) -> list[BenchmarkEntry]:
        """Benchmark algorithms on a list of city pairs.

        Args:
            city_pairs: List of (source, target) tuples.
            algorithms: List of algorithm names to test. Defaults to all
                four: ['dijkstra', 'astar', 'bfs', 'bellman_ford'].

        Returns:
            List of :class:`BenchmarkEntry` results.
        """
        if algorithms is None:
            algorithms = ["dijkstra", "astar", "bfs", "bellman_ford"]

        algo_map = {
            "dijkstra": self.finder.dijkstra,
            "astar": self.finder.astar,
            "bfs": self.finder.bfs,
            "bellman_ford": self.finder.bellman_ford,
        }

        self.results = []

        for source, target in city_pairs:
            for algo_name in algorithms:
                func = algo_map.get(algo_name)
                if func is None:
                    continue
                result = func(source, target)
                entry = BenchmarkEntry(
                    source=source,
                    target=target,
                    algorithm=result.algorithm,
                    distance_km=result.distance_km,
                    nodes_explored=result.nodes_explored,
                    execution_time_ms=result.execution_time_ms,
                    path_length=len(result.path),
                    found=result.found,
                )
                self.results.append(entry)

        return self.results

    def generate_report(self, results: list[BenchmarkEntry] = None) -> str:
        """Generate a Markdown-formatted benchmark report.

        Args:
            results: Benchmark entries to include. Defaults to the last
                run's results.

        Returns:
            A Markdown string with tables and summary statistics.
        """
        if results is None:
            results = self.results

        if not results:
            return "No benchmark results available."

        lines = ["# Algorithm Benchmark Report\n"]

        # Group by city pair
        pairs = {}
        for entry in results:
            key = (entry.source, entry.target)
            pairs.setdefault(key, []).append(entry)

        for (src, tgt), entries in pairs.items():
            lines.append(f"## {src} -> {tgt}\n")
            lines.append(
                "| Algorithm | Distance (km) | Nodes Explored | "
                "Time (ms) | Path Length |"
            )
            lines.append(
                "|-----------|--------------|----------------|"
                "-----------|-------------|"
            )
            for e in entries:
                dist = f"{e.distance_km:.2f}" if e.found else "N/A"
                lines.append(
                    f"| {e.algorithm} | {dist} | {e.nodes_explored} | "
                    f"{e.execution_time_ms:.3f} | {e.path_length} |"
                )
            lines.append("")

        # Summary statistics
        lines.append("## Summary\n")
        algo_times = {}
        for entry in results:
            algo_times.setdefault(entry.algorithm, []).append(
                entry.execution_time_ms
            )

        lines.append("| Algorithm | Avg Time (ms) | Min Time (ms) | Max Time (ms) |")
        lines.append("|-----------|--------------|--------------|--------------|")
        for algo, times in algo_times.items():
            avg_t = sum(times) / len(times)
            min_t = min(times)
            max_t = max(times)
            lines.append(
                f"| {algo} | {avg_t:.3f} | {min_t:.3f} | {max_t:.3f} |"
            )

        return "\n".join(lines)

    def plot_comparison(self, results: list[BenchmarkEntry] = None,
                        output_path: str = None):
        """Create a matplotlib bar chart comparing algorithm execution times.

        Args:
            results: Benchmark entries. Defaults to last run's results.
            output_path: If provided, save figure to this path. Otherwise
                calls ``plt.show()``.

        Returns:
            The matplotlib Figure, or None if matplotlib is unavailable.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("matplotlib and numpy are required for plotting.")
            return None

        if results is None:
            results = self.results

        if not results:
            print("No benchmark results to plot.")
            return None

        # Group by city pair and algorithm
        pairs = {}
        for entry in results:
            key = f"{entry.source} -> {entry.target}"
            pairs.setdefault(key, {})[entry.algorithm] = entry.execution_time_ms

        algo_names = sorted({e.algorithm for e in results})
        pair_labels = list(pairs.keys())

        x = np.arange(len(pair_labels))
        width = 0.8 / len(algo_names)
        colors = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#E91E63"]

        fig, ax = plt.subplots(figsize=(12, 6))

        for i, algo in enumerate(algo_names):
            times = [pairs[pair].get(algo, 0) for pair in pair_labels]
            offset = (i - len(algo_names) / 2 + 0.5) * width
            ax.bar(x + offset, times, width, label=algo,
                   color=colors[i % len(colors)], alpha=0.85)

        ax.set_xlabel("City Pair")
        ax.set_ylabel("Execution Time (ms)")
        ax.set_title("Algorithm Performance Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(pair_labels, rotation=30, ha="right")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()

        if output_path:
            fig.savefig(output_path, dpi=150)
            print(f"Chart saved to {output_path}")
        else:
            plt.show()

        return fig
