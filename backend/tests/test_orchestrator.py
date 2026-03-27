# backend/tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch
from app.scrapers.orchestrator import ScrapingOrchestrator
from app.scrapers.base import RawTicketListing


@pytest.mark.asyncio
async def test_orchestrator_runs_all_scrapers():
    mock_listing = RawTicketListing(
        source_site="test", source_url="https://test.com/1",
        source_section_name="Test Stand", ticket_type="weekend",
        price=100.0, currency="EUR",
    )
    mock_scraper = AsyncMock()
    mock_scraper.scrape_circuit = AsyncMock(return_value=[mock_listing])
    mock_scraper.source_site = "test"
    mock_scraper.random_delay = AsyncMock()

    orchestrator = ScrapingOrchestrator(scrapers=[mock_scraper])

    with patch.object(orchestrator, '_get_circuits_and_events') as mock_get:
        mock_get.return_value = [
            {"circuit_id": 1, "circuit_name": "Test Circuit", "race_name": "Test GP", "country": "Test", "event_id": 1}
        ]
        with patch.object(orchestrator, '_save_listings', return_value=(1, 0)) as mock_save:
            with patch.object(orchestrator, '_build_section_map', return_value={}):
                results = await orchestrator.run()

    assert mock_scraper.scrape_circuit.call_count == 1
    assert mock_save.call_count == 1
    assert results["total_listings"] == 1


@pytest.mark.asyncio
async def test_orchestrator_handles_scraper_failure():
    mock_scraper = AsyncMock()
    mock_scraper.scrape_circuit = AsyncMock(side_effect=Exception("Connection failed"))
    mock_scraper.source_site = "failing_source"
    mock_scraper.random_delay = AsyncMock()

    orchestrator = ScrapingOrchestrator(scrapers=[mock_scraper])

    with patch.object(orchestrator, '_get_circuits_and_events') as mock_get:
        mock_get.return_value = [
            {"circuit_id": 1, "circuit_name": "Test", "race_name": "Test GP", "country": "Test", "event_id": 1}
        ]
        with patch.object(orchestrator, '_save_listings'):
            with patch.object(orchestrator, '_build_section_map', return_value={}):
                results = await orchestrator.run()

    assert results["errors"] == 1


@pytest.mark.asyncio
async def test_circuit_breaker_trips_after_3_failures():
    mock_scraper = AsyncMock()
    mock_scraper.scrape_circuit = AsyncMock(side_effect=Exception("Fail"))
    mock_scraper.source_site = "fragile"
    mock_scraper.random_delay = AsyncMock()

    orchestrator = ScrapingOrchestrator(scrapers=[mock_scraper])

    circuits = [
        {"circuit_id": i, "circuit_name": f"Circuit {i}", "race_name": f"GP {i}", "country": "Test", "event_id": i}
        for i in range(1, 6)
    ]

    with patch.object(orchestrator, '_get_circuits_and_events', return_value=circuits):
        with patch.object(orchestrator, '_save_listings'):
            with patch.object(orchestrator, '_build_section_map', return_value={}):
                results = await orchestrator.run()

    # Should trip after 3 failures, not attempt all 5
    assert mock_scraper.scrape_circuit.call_count == 3
    assert results["errors"] == 3
