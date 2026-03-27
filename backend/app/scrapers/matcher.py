"""Fuzzy matching engine for mapping scraped section names to seat_section IDs."""

import logging
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

MATCH_THRESHOLD = 70


def match_section_name(
    source_name: str,
    section_map: dict[str, int],
) -> int | None:
    """Match a scraped section name to a known seat section.

    Returns the seat_section_id if a match is found, None otherwise.
    """
    if not section_map:
        return None

    # Try exact match first (case-insensitive)
    source_lower = source_name.lower().strip()
    for name, sid in section_map.items():
        if name.lower().strip() == source_lower:
            return sid

    # Fuzzy match
    result = process.extractOne(
        source_name,
        section_map.keys(),
        scorer=fuzz.token_set_ratio,
        score_cutoff=MATCH_THRESHOLD,
    )

    if result is None:
        logger.debug(f"No match for '{source_name}' (threshold={MATCH_THRESHOLD})")
        return None

    matched_name, score, _ = result
    logger.debug(f"Matched '{source_name}' -> '{matched_name}' (score={score})")
    return section_map[matched_name]
