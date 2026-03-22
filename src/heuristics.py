"""Heuristic functions for the A* search algorithm.

All heuristic functions take two coordinate tuples (lat, lon) and return
an estimated distance in kilometers.
"""

import math


# Earth's mean radius in kilometers
_EARTH_RADIUS_KM = 6371.0


def haversine(coord1: tuple, coord2: tuple) -> float:
    """Calculate the great-circle distance between two points on Earth.

    Uses the Haversine formula for accurate distance on a sphere.

    Args:
        coord1: (latitude, longitude) in decimal degrees.
        coord2: (latitude, longitude) in decimal degrees.

    Returns:
        Distance in kilometers.
    """
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return _EARTH_RADIUS_KM * c


def euclidean(coord1: tuple, coord2: tuple) -> float:
    """Euclidean distance using degree differences scaled to approximate km.

    This is a rough approximation that treats latitude and longitude as
    a flat plane. One degree of latitude is approximately 111 km.

    Args:
        coord1: (latitude, longitude) in decimal degrees.
        coord2: (latitude, longitude) in decimal degrees.

    Returns:
        Approximate distance in kilometers.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Scale longitude by cosine of average latitude
    avg_lat = math.radians((lat1 + lat2) / 2.0)
    dx = (lon2 - lon1) * math.cos(avg_lat) * 111.0
    dy = (lat2 - lat1) * 111.0

    return math.sqrt(dx * dx + dy * dy)


def manhattan(coord1: tuple, coord2: tuple) -> float:
    """Manhattan distance using degree differences scaled to approximate km.

    Args:
        coord1: (latitude, longitude) in decimal degrees.
        coord2: (latitude, longitude) in decimal degrees.

    Returns:
        Approximate distance in kilometers.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    avg_lat = math.radians((lat1 + lat2) / 2.0)
    dx = abs(lon2 - lon1) * math.cos(avg_lat) * 111.0
    dy = abs(lat2 - lat1) * 111.0

    return dx + dy


def zero_heuristic(coord1: tuple, coord2: tuple) -> float:
    """Zero heuristic - always returns 0.

    When used with A*, this makes it behave identically to Dijkstra's
    algorithm, since f(n) = g(n) + 0 = g(n).

    Args:
        coord1: Ignored.
        coord2: Ignored.

    Returns:
        0.0
    """
    return 0.0


# Registry of available heuristics for easy lookup
HEURISTICS = {
    "haversine": haversine,
    "euclidean": euclidean,
    "manhattan": manhattan,
    "zero": zero_heuristic,
}


def get_heuristic(name: str):
    """Get a heuristic function by name.

    Args:
        name: One of 'haversine', 'euclidean', 'manhattan', 'zero'.

    Returns:
        The heuristic function.

    Raises:
        ValueError: If the heuristic name is unknown.
    """
    if name not in HEURISTICS:
        raise ValueError(
            f"Unknown heuristic '{name}'. Choose from: {list(HEURISTICS.keys())}"
        )
    return HEURISTICS[name]
