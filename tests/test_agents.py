
import pytest
from retail_warehouse_scraper.src.agents.analysis_agent import AnalysisAgent
from retail_warehouse_scraper.src.agents.research_agent import ResearchAgent
from retail_warehouse_scraper.src.agents.scraping_agent import ScrapingAgent
from retail_warehouse_scraper.src.models.company import BusinessVertical, ScrapedData, SearchQuery


@pytest.mark.asyncio
async def test_research_agent_research_company(monkeypatch):
    agent = ResearchAgent(api_key="test")
    async def mock_run(query, deps=None):
        class Result:
            data = ["https://example.com"]
        return Result()
    monkeypatch.setattr(agent.agent, "run", mock_run)
    query = SearchQuery(company_name="Test Company", vertical=BusinessVertical.GROCERY)
    urls = await agent.research_company(query)
    assert "https://example.com" in urls

@pytest.mark.asyncio
async def test_scraping_agent_scrape_urls(monkeypatch):
    agent = ScrapingAgent(api_key="test", firecrawl_api_key="test")
    async def mock_run(url):
        class Result:
            data = ScrapedData(url="https://example.com", content="Test", extracted_data={}, scrape_timestamp=None)
        return Result()
    monkeypatch.setattr(agent.agent, "run", mock_run)
    results = await agent.scrape_urls(["https://example.com"])
    assert results[0].url == "https://example.com"

@pytest.mark.asyncio
async def test_analysis_agent_analyze_company_data(monkeypatch):
    agent = AnalysisAgent(api_key="test")
    async def mock_run(content, deps=None):
        class Result:
            class Data:
                company_name = "Test Company"
                cleaned_name = "test company"
                vertical = BusinessVertical.GROCERY
                truck_count = 10
                warehouse_employee_count = 50
                facility_count = 2
                store_count = 5
                notes = "Test notes"
                source_references = ["https://example.com"]
                last_updated = None
                confidence_score = 0.9
            data = Data()
        return Result()
    monkeypatch.setattr(agent.agent, "run", mock_run)
    query = SearchQuery(company_name="Test Company", vertical=BusinessVertical.GROCERY)
    scraped_data = []
    result = await agent.analyze_company_data(query, scraped_data)
    assert result.company_name == "Test Company"
