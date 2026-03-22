"""Map visualization of routes using Folium."""

import folium


# Colour palette for different algorithm routes
_ALGORITHM_COLORS = {
    "Dijkstra": "#2196F3",       # Blue
    "A*": "#4CAF50",             # Green
    "BFS": "#FF9800",            # Orange
    "Bellman-Ford": "#9C27B0",   # Purple
}

_DEFAULT_COLORS = [
    "#E91E63", "#00BCD4", "#FF5722", "#795548",
    "#607D8B", "#3F51B5", "#009688", "#CDDC39",
]


class RouteVisualizer:
    """Visualize cities and routes on an interactive Folium map.

    Args:
        center_lat: Latitude for the initial map centre.
        center_lon: Longitude for the initial map centre.
        zoom: Initial zoom level.
    """

    def __init__(self, center_lat: float = 35.0, center_lon: float = 3.0,
                 zoom: int = 6):
        self._map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles="OpenStreetMap",
        )
        self._color_idx = 0

    def _next_color(self):
        color = _DEFAULT_COLORS[self._color_idx % len(_DEFAULT_COLORS)]
        self._color_idx += 1
        return color

    def add_cities(self, cities_dict: dict, color: str = "red",
                   radius: int = 6) -> "RouteVisualizer":
        """Add city markers to the map.

        Args:
            cities_dict: Dict of city_name -> (lat, lon).
            color: Marker fill colour.
            radius: Marker radius in pixels.

        Returns:
            Self, for method chaining.
        """
        for city, (lat, lon) in cities_dict.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"<b>{city}</b><br>({lat:.4f}, {lon:.4f})",
                tooltip=city,
                color="black",
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
            ).add_to(self._map)
        return self

    def add_route(self, path: list, coords_dict: dict,
                  color: str = None, label: str = "",
                  weight: int = 4, opacity: float = 0.8) -> "RouteVisualizer":
        """Add a route polyline to the map.

        Args:
            path: Ordered list of city names forming the route.
            coords_dict: Dict of city_name -> (lat, lon).
            color: Line colour. Auto-assigned if None.
            label: Label for the route (shown in popup).
            weight: Line weight in pixels.
            opacity: Line opacity (0-1).

        Returns:
            Self, for method chaining.
        """
        if len(path) < 2:
            return self

        if color is None:
            color = self._next_color()

        locations = [[coords_dict[city][0], coords_dict[city][1]]
                     for city in path if city in coords_dict]

        popup_text = f"<b>{label}</b><br>{' &#8594; '.join(str(c) for c in path)}"

        folium.PolyLine(
            locations=locations,
            color=color,
            weight=weight,
            opacity=opacity,
            popup=popup_text,
            tooltip=label or "Route",
        ).add_to(self._map)

        # Mark start and end
        if path[0] in coords_dict:
            folium.Marker(
                location=list(coords_dict[path[0]]),
                popup=f"Start: {path[0]}",
                icon=folium.Icon(color="green", icon="play", prefix="fa"),
            ).add_to(self._map)

        if path[-1] in coords_dict:
            folium.Marker(
                location=list(coords_dict[path[-1]]),
                popup=f"End: {path[-1]}",
                icon=folium.Icon(color="red", icon="stop", prefix="fa"),
            ).add_to(self._map)

        return self

    def add_multiple_routes(self, results: dict, coords_dict: dict,
                            weight: int = 4) -> "RouteVisualizer":
        """Overlay routes from multiple algorithms.

        Args:
            results: Dict of algorithm_name -> PathResult.
            coords_dict: Dict of city_name -> (lat, lon).
            weight: Base line weight.

        Returns:
            Self, for method chaining.
        """
        offset = 0
        for algo_name, result in results.items():
            if not result.found:
                continue
            color = _ALGORITHM_COLORS.get(algo_name, self._next_color())
            label = f"{algo_name}: {result.distance_km:.1f} km"
            self.add_route(
                path=result.path,
                coords_dict=coords_dict,
                color=color,
                label=label,
                weight=weight - offset,
                opacity=0.7,
            )
            offset = min(offset + 1, weight - 1)

        return self

    def add_graph_edges(self, graph, coords_dict: dict,
                        color: str = "#CCCCCC", weight: int = 1,
                        opacity: float = 0.3) -> "RouteVisualizer":
        """Draw all edges of the graph as thin lines.

        Args:
            graph: A NetworkX graph.
            coords_dict: Dict of node_name -> (lat, lon).
            color: Edge colour.
            weight: Edge line weight.
            opacity: Edge opacity.

        Returns:
            Self, for method chaining.
        """
        for u, v in graph.edges():
            if u in coords_dict and v in coords_dict:
                folium.PolyLine(
                    locations=[
                        [coords_dict[u][0], coords_dict[u][1]],
                        [coords_dict[v][0], coords_dict[v][1]],
                    ],
                    color=color,
                    weight=weight,
                    opacity=opacity,
                ).add_to(self._map)
        return self

    def add_comparison_legend(self, results: dict) -> "RouteVisualizer":
        """Add a legend showing algorithm comparison metrics.

        Args:
            results: Dict of algorithm_name -> PathResult.

        Returns:
            Self, for method chaining.
        """
        legend_html = """
        <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
             background: white; padding: 12px 16px; border-radius: 8px;
             box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-family: Arial;
             font-size: 13px; max-width: 350px;">
            <b style="font-size: 14px;">Algorithm Comparison</b><br>
            <table style="margin-top:6px; border-collapse:collapse;">
                <tr style="border-bottom:1px solid #ddd;">
                    <th style="text-align:left; padding:3px 8px;">Algorithm</th>
                    <th style="text-align:right; padding:3px 8px;">Distance</th>
                    <th style="text-align:right; padding:3px 8px;">Time</th>
                </tr>
        """
        for algo_name, result in results.items():
            color = _ALGORITHM_COLORS.get(algo_name, "#333")
            dist = f"{result.distance_km:.1f} km" if result.found else "N/A"
            legend_html += f"""
                <tr>
                    <td style="padding:3px 8px;">
                        <span style="color:{color};">&#9632;</span> {algo_name}
                    </td>
                    <td style="text-align:right; padding:3px 8px;">{dist}</td>
                    <td style="text-align:right; padding:3px 8px;">
                        {result.execution_time_ms:.2f} ms
                    </td>
                </tr>
            """
        legend_html += "</table></div>"

        self._map.get_root().html.add_child(folium.Element(legend_html))
        return self

    def save(self, output_path: str = "map.html") -> str:
        """Save the map to an HTML file.

        Args:
            output_path: File path for the output HTML.

        Returns:
            The output path.
        """
        self._map.save(output_path)
        return output_path

    def get_map(self) -> folium.Map:
        """Return the underlying Folium Map object."""
        return self._map
