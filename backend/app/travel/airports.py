"""
City-to-airport mapping for F1 circuit cities and major world cities.
Each entry maps a lowercase city name to a (IATA_code, country) tuple.
"""
from typing import Optional

# Keys are lowercase city names for case-insensitive lookup
CITY_AIRPORTS: dict[str, tuple[str, str]] = {
    # F1 circuit cities
    "melbourne": ("MEL", "Australia"),
    "shanghai": ("PVG", "China"),
    "suzuka": ("NGO", "Japan"),
    "bahrain": ("BAH", "Bahrain"),
    "jeddah": ("JED", "Saudi Arabia"),
    "miami": ("MIA", "United States"),
    "monaco": ("NCE", "France"),         # nearest airport: Nice
    "montreal": ("YUL", "Canada"),
    "barcelona": ("BCN", "Spain"),
    "spielberg": ("GRZ", "Austria"),     # Red Bull Ring, nearest: Graz
    "silverstone": ("BHX", "United Kingdom"),  # nearest: Birmingham
    "budapest": ("BUD", "Hungary"),
    "spa": ("LGG", "Belgium"),           # nearest: Liege
    "zandvoort": ("AMS", "Netherlands"), # nearest: Amsterdam
    "monza": ("MXP", "Italy"),           # nearest: Milan Malpensa
    "baku": ("GYD", "Azerbaijan"),
    "singapore": ("SIN", "Singapore"),
    "austin": ("AUS", "United States"),
    "mexico city": ("MEX", "Mexico"),
    "sao paulo": ("GRU", "Brazil"),
    "las vegas": ("LAS", "United States"),
    "lusail": ("DOH", "Qatar"),          # nearest: Doha
    "abu dhabi": ("AUH", "United Arab Emirates"),
    "imola": ("BLQ", "Italy"),           # nearest: Bologna
    "portimao": ("FAO", "Portugal"),     # nearest: Faro
    "istanbul": ("IST", "Turkey"),
    "mugello": ("FLR", "Italy"),         # nearest: Florence
    "nurburgring": ("CGN", "Germany"),   # nearest: Cologne
    "sochi": ("AER", "Russia"),
    "riyadh": ("RUH", "Saudi Arabia"),
    "doha": ("DOH", "Qatar"),

    # Major world cities
    "london": ("LHR", "United Kingdom"),
    "paris": ("CDG", "France"),
    "new york": ("JFK", "United States"),
    "los angeles": ("LAX", "United States"),
    "chicago": ("ORD", "United States"),
    "toronto": ("YYZ", "Canada"),
    "sydney": ("SYD", "Australia"),
    "tokyo": ("HND", "Japan"),
    "osaka": ("KIX", "Japan"),
    "beijing": ("PEK", "China"),
    "hong kong": ("HKG", "Hong Kong"),
    "seoul": ("ICN", "South Korea"),
    "dubai": ("DXB", "United Arab Emirates"),
    "frankfurt": ("FRA", "Germany"),
    "amsterdam": ("AMS", "Netherlands"),
    "madrid": ("MAD", "Spain"),
    "rome": ("FCO", "Italy"),
    "milan": ("MXP", "Italy"),
    "zurich": ("ZRH", "Switzerland"),
    "vienna": ("VIE", "Austria"),
    "brussels": ("BRU", "Belgium"),
    "stockholm": ("ARN", "Sweden"),
    "oslo": ("OSL", "Norway"),
    "copenhagen": ("CPH", "Denmark"),
    "helsinki": ("HEL", "Finland"),
    "warsaw": ("WAW", "Poland"),
    "prague": ("PRG", "Czech Republic"),
    "athens": ("ATH", "Greece"),
    "lisbon": ("LIS", "Portugal"),
    "johannesburg": ("JNB", "South Africa"),
    "cape town": ("CPT", "South Africa"),
    "nairobi": ("NBO", "Kenya"),
    "cairo": ("CAI", "Egypt"),
    "casablanca": ("CMN", "Morocco"),
    "mumbai": ("BOM", "India"),
    "delhi": ("DEL", "India"),
    "bangalore": ("BLR", "India"),
    "kuala lumpur": ("KUL", "Malaysia"),
    "bangkok": ("BKK", "Thailand"),
    "jakarta": ("CGK", "Indonesia"),
    "manila": ("MNL", "Philippines"),
    "taipei": ("TPE", "Taiwan"),
    "auckland": ("AKL", "New Zealand"),
    "buenos aires": ("EZE", "Argentina"),
    "bogota": ("BOG", "Colombia"),
    "lima": ("LIM", "Peru"),
    "santiago": ("SCL", "Chile"),
    "johannesburg": ("JNB", "South Africa"),
    "moscow": ("SVO", "Russia"),
    "amsterdam": ("AMS", "Netherlands"),
    "munich": ("MUC", "Germany"),
    "berlin": ("BER", "Germany"),
    "dallas": ("DFW", "United States"),
    "atlanta": ("ATL", "United States"),
    "seattle": ("SEA", "United States"),
    "san francisco": ("SFO", "United States"),
    "boston": ("BOS", "United States"),
    "washington": ("IAD", "United States"),
    "vancouver": ("YVR", "Canada"),
}

# Remove duplicate keys that may have been added accidentally (Python dicts keep last value)
# The dict is already deduplicated by Python's dict semantics


def lookup_airport(city: str) -> Optional[tuple[str, str]]:
    """
    Look up the nearest IATA airport code and country for a given city name.

    Args:
        city: City name (case-insensitive).

    Returns:
        A (IATA_code, country) tuple if found, or None if the city is unknown.
    """
    return CITY_AIRPORTS.get(city.strip().lower())


def get_city_suggestions() -> list[str]:
    """
    Return the list of all known city names (in their canonical lowercase form).

    Returns:
        Sorted list of city name strings.
    """
    return sorted(CITY_AIRPORTS.keys())
