# Shortest Path Algeria

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Algorithms](https://img.shields.io/badge/Algorithms-4-orange)

Find the shortest path between Algerian cities using **A\***, **Dijkstra**, **BFS**, and **Bellman-Ford** algorithms on real OpenStreetMap data. Visualize routes on interactive maps with [Folium](https://python-visualization.github.io/folium/).

## Features

- **4 pathfinding algorithms** implemented from scratch (not wrappers around NetworkX)
- **35+ Algerian cities** from the Mediterranean coast to the Sahara
- **Interactive map visualization** with Folium (pan, zoom, click for details)
- **Algorithm benchmarking** with execution time, nodes explored, and path optimality comparisons
- **Multiple heuristics** for A*: Haversine, Euclidean, Manhattan
- **Synthetic road network** using Haversine distance with road factor estimation
- **Optional OSM integration** for real road network data via `osmnx`

## Algorithm Comparison

| Algorithm | Time Complexity | Space Complexity | Optimal? | Notes |
|-----------|----------------|-----------------|----------|-------|
| **Dijkstra** | O((V+E) log V) | O(V) | Yes | Gold standard for non-negative weights |
| **A\*** | O((V+E) log V) | O(V) | Yes* | Faster than Dijkstra with admissible heuristic |
| **BFS** | O(V + E) | O(V) | No** | Finds fewest-hop path, ignores weights |
| **Bellman-Ford** | O(V * E) | O(V) | Yes | Handles negative weights, detects negative cycles |

\* With an admissible and consistent heuristic (Haversine qualifies).
\** Optimal for unweighted graphs only.

## Quick Start

### Installation

```bash
git clone https://github.com/kadirou12333/shortest-path-algeria.git
cd shortest-path-algeria
pip install -r requirements.txt
```

### Find a Route

```bash
python examples/find_route.py --from "Oran" --to "Constantine" --algorithm astar
```

### Compare All Algorithms

```bash
python examples/compare_algorithms.py --from "Oran" --to "Algiers"
```

### Run Tests

```bash
pytest tests/ -v
```

## Usage

### Python API

```python
from src.cities import ALGERIAN_CITIES
from src.graph_builder import GraphBuilder
from src.algorithms import PathFinder, format_comparison_table

# Build the road network
builder = GraphBuilder()
graph = builder.build_synthetic(ALGERIAN_CITIES)

# Find shortest path
finder = PathFinder(graph)
result = finder.astar("Algiers", "Tamanrasset")
print(result.summary())

# Compare all algorithms
results = finder.compare_all("Oran", "Constantine")
print(format_comparison_table(results))
```

### Map Visualization

```python
from src.visualizer import RouteVisualizer

viz = RouteVisualizer()
viz.add_cities(ALGERIAN_CITIES)
viz.add_route(result.path, ALGERIAN_CITIES, label="A*")
viz.save("my_route.html")
```

## Sample Output

```
-----------------------------------------------------------------------
Algorithm        Distance (km)  Nodes Explored   Time (ms)  Path Length
-----------------------------------------------------------------------
Dijkstra               668.42              22       0.150           5
A*                     668.42               8       0.085           5
BFS                    723.10              18       0.045           4
Bellman-Ford           668.42             410       1.230           5
-----------------------------------------------------------------------
```

## City Coverage

The database includes **35 cities** across all regions of Algeria:

- **Mediterranean Coast**: Algiers, Oran, Annaba, Constantine, Skikda, Jijel, Mostaganem
- **Northern Inland**: Blida, Tizi Ouzou, Chlef, Tiaret, Tlemcen, Sidi Bel Abbes
- **High Plateaus**: Batna, Djelfa, Biskra, M'sila, Tebessa
- **Sahara**: Ghardaia, Ouargla, Bechar, Adrar, Tamanrasset, In Salah, Illizi, Tindouf

## Adding New Cities

Edit `src/cities.py` and add entries to the `ALGERIAN_CITIES` dictionary:

```python
ALGERIAN_CITIES["NewCity"] = (latitude, longitude)
```

Coordinates can be found on [OpenStreetMap](https://www.openstreetmap.org/) or Google Maps.

## Interactive Notebook

Open the Jupyter notebook for a guided walkthrough:

```bash
jupyter notebook notebooks/shortest_path_demo.ipynb
```

## Project Structure

```
shortest-path-algeria/
├── src/
│   ├── algorithms.py       # Dijkstra, A*, BFS, Bellman-Ford
│   ├── benchmarks.py       # Performance comparison tools
│   ├── cities.py           # Algerian city coordinates database
│   ├── graph_builder.py    # Build road network graphs
│   ├── heuristics.py       # Heuristic functions for A*
│   └── visualizer.py       # Folium map visualization
├── examples/
│   ├── find_route.py       # CLI: find a single route
│   └── compare_algorithms.py  # CLI: compare all algorithms
├── notebooks/
│   └── shortest_path_demo.ipynb  # Interactive demo
├── tests/
│   └── test_algorithms.py  # Unit tests
└── results/                # Generated maps and charts
```

## References

- Cormen, Leiserson, Rivest, Stein - *Introduction to Algorithms* (Dijkstra, Bellman-Ford, BFS)
- Hart, Nilsson, Raphael (1968) - *A Formal Basis for the Heuristic Determination of Minimum Cost Paths* (A* algorithm)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula) - great-circle distance calculation
- [OpenStreetMap](https://www.openstreetmap.org/) - map data
- [Folium](https://python-visualization.github.io/folium/) - interactive map visualization
- [NetworkX](https://networkx.org/) - graph data structures

## License

[MIT](LICENSE)
