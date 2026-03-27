from app.scrapers.matcher import match_section_name


def test_exact_match():
    sections = {"Central Grandstand": 1, "GA Zone A": 2}
    result = match_section_name("Central Grandstand", sections)
    assert result == 1


def test_fuzzy_match():
    sections = {"Wellington Straight": 1, "Copse Grandstand": 2}
    result = match_section_name("Wellington Straight Grandstand", sections)
    assert result == 1


def test_case_insensitive():
    sections = {"Abbey Grandstand": 1}
    result = match_section_name("abbey grandstand", sections)
    assert result == 1


def test_no_match():
    sections = {"Wellington Straight": 1, "Copse Grandstand": 2}
    result = match_section_name("Completely Unknown Section XYZ", sections)
    assert result is None


def test_partial_match():
    sections = {"Copse A": 1, "Copse B": 2, "Copse C": 3}
    result = match_section_name("Copse A Grandstand", sections)
    assert result == 1
