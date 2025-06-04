
import pytest
from retail_warehouse_scraper.src.tools.firecrawl_client import FirecrawlClient
from retail_warehouse_scraper.src.tools.web_search import search_company_info


@pytest.mark.asyncio
async def test_search_company_info_mock(monkeypatch):
    async def mock_search_company_info(query):
        return [{"title": "Test", "url": "https://example.com", "snippet": "Test snippet"}]
    monkeypatch.setattr("retail_warehouse_scraper.src.tools.web_search.search_company_info", mock_search_company_info)
    results = await search_company_info("Test Company")
    assert results[0]["url"] == "https://example.com"

@pytest.mark.asyncio
async def test_firecrawl_client_scrape_mock(monkeypatch):
    client = FirecrawlClient()
    async def mock_scrape(url, params=None):
        return {"content": "Test content", "url": url, "status_code": 200}
    monkeypatch.setattr(client, "scrape", mock_scrape)
    result = await client.scrape("https://example.com")
    assert result["status_code"] == 200
