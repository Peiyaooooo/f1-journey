from app.travel.airports import lookup_airport, get_city_suggestions


def test_lookup_known_city():
    result = lookup_airport("London")
    assert result is not None
    iata, country = result
    assert iata == "LHR"
    assert country == "United Kingdom"


def test_lookup_case_insensitive():
    # Test various case forms
    assert lookup_airport("TOKYO") == lookup_airport("tokyo")
    assert lookup_airport("Monaco") == lookup_airport("monaco")
    assert lookup_airport("SaO PaUlO") == lookup_airport("sao paulo")

    result = lookup_airport("TOKYO")
    assert result is not None
    assert result[0] == "HND"


def test_lookup_unknown_city():
    result = lookup_airport("Atlantis")
    assert result is None

    result = lookup_airport("   ")
    assert result is None

    result = lookup_airport("NonExistentCity123")
    assert result is None


def test_get_suggestions():
    cities = get_city_suggestions()
    assert len(cities) >= 50

    # Should be a sorted list
    assert cities == sorted(cities)

    # Key F1 circuit cities must be present
    f1_cities = [
        "melbourne", "monaco", "montreal", "singapore",
        "monza", "silverstone", "spa", "budapest",
        "baku", "abu dhabi", "miami", "las vegas",
    ]
    for city in f1_cities:
        assert city in cities, f"F1 city '{city}' missing from suggestions"

    # Key world cities must be present
    world_cities = [
        "london", "paris", "new york", "tokyo", "dubai",
        "sydney", "frankfurt", "beijing", "seoul",
    ]
    for city in world_cities:
        assert city in cities, f"World city '{city}' missing from suggestions"
