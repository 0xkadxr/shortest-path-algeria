"""Database of major Algerian cities with GPS coordinates (latitude, longitude)."""

ALGERIAN_CITIES = {
    # Northern Algeria - Mediterranean Coast
    "Algiers": (36.7538, 3.0588),
    "Oran": (35.6969, -0.6331),
    "Constantine": (36.3650, 6.6147),
    "Annaba": (36.9000, 7.7667),
    "Béjaïa": (36.7500, 5.0667),
    "Mostaganem": (35.9333, 0.0833),
    "Skikda": (36.8667, 6.9000),
    "Jijel": (36.8208, 5.7667),

    # Northern Algeria - Inland
    "Blida": (36.4700, 2.8300),
    "Sétif": (36.1900, 5.4100),
    "Sidi Bel Abbès": (35.1897, -0.6308),
    "Tlemcen": (34.8828, -1.3167),
    "Tizi Ouzou": (36.7169, 4.0497),
    "Médéa": (36.2675, 2.7500),
    "Chlef": (36.1647, 1.3317),
    "Tiaret": (35.3711, 1.3172),
    "Bouira": (36.3800, 3.9000),

    # Hauts Plateaux (High Plateaus)
    "Batna": (35.5500, 6.1667),
    "Djelfa": (34.6700, 3.2500),
    "Biskra": (34.8500, 5.7333),
    "Tébessa": (35.4000, 8.1167),
    "M'sila": (35.7000, 4.5500),
    "Bordj Bou Arreridj": (36.0667, 4.7667),
    "Saïda": (34.8303, 0.1531),

    # Southern Algeria - Sahara
    "Ghardaia": (32.4900, 3.6700),
    "Ouargla": (31.9500, 5.3167),
    "Béchar": (31.6167, -2.2167),
    "Adrar": (27.8742, -0.2939),
    "Tamanrasset": (22.7850, 5.5228),
    "In Salah": (27.1928, 2.4672),
    "El Oued": (33.3681, 6.8675),
    "Touggourt": (33.1000, 6.0667),
    "Illizi": (26.5000, 8.4833),
    "Tindouf": (27.6744, -8.1478),
    "Hassi Messaoud": (31.6800, 6.0700),
}


def get_city_coords(city_name: str) -> tuple:
    """Get (lat, lon) coordinates for a city.

    Args:
        city_name: Name of the Algerian city.

    Returns:
        Tuple of (latitude, longitude).

    Raises:
        KeyError: If the city is not found in the database.
    """
    if city_name not in ALGERIAN_CITIES:
        available = ", ".join(sorted(ALGERIAN_CITIES.keys()))
        raise KeyError(
            f"City '{city_name}' not found. Available cities: {available}"
        )
    return ALGERIAN_CITIES[city_name]


def list_cities() -> list:
    """Return a sorted list of all available city names."""
    return sorted(ALGERIAN_CITIES.keys())


def get_region_cities(region: str) -> dict:
    """Get cities by rough geographical region.

    Args:
        region: One of 'north', 'highlands', 'south'.

    Returns:
        Dict of city_name -> (lat, lon) for cities in the region.
    """
    regions = {
        "north": [
            "Algiers", "Oran", "Constantine", "Annaba", "Béjaïa",
            "Mostaganem", "Skikda", "Jijel", "Blida", "Sétif",
            "Sidi Bel Abbès", "Tlemcen", "Tizi Ouzou", "Médéa",
            "Chlef", "Tiaret", "Bouira",
        ],
        "highlands": [
            "Batna", "Djelfa", "Biskra", "Tébessa", "M'sila",
            "Bordj Bou Arreridj", "Saïda",
        ],
        "south": [
            "Ghardaia", "Ouargla", "Béchar", "Adrar", "Tamanrasset",
            "In Salah", "El Oued", "Touggourt", "Illizi", "Tindouf",
            "Hassi Messaoud",
        ],
    }
    region = region.lower()
    if region not in regions:
        raise ValueError(f"Region must be one of: {list(regions.keys())}")
    return {city: ALGERIAN_CITIES[city] for city in regions[region]}
