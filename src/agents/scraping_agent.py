import asyncio
from typing import Any, Dict, List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from ..models.company import ScrapedData
from ..tools.firecrawl_client import FirecrawlClient


class ScrapingAgent:
    def __init__(self, api_key: str, firecrawl_api_key: str):
        self.model = OpenAIModel("gpt-4-turbo-preview", api_key=api_key)
        self.firecrawl = FirecrawlClient(api_key=firecrawl_api_key)

        self.agent = Agent(
            self.model,
            output_type=ScrapedData,
            system_prompt="""You are a web scraping specialist. Extract structured data from web pages about companies.
            Focus on finding:
            - Fleet/truck counts (look for numbers with words like 'trucks', 'fleet', 'vehicles')
            - Employee counts (especially warehouse/distribution center employees)
            - Facility/warehouse/distribution center counts
            - Store/location counts
            - Any other relevant operational metrics

            Return structured data with the specific numbers found.""",
        )

        @self.agent.tool_plain
        async def scrape_url(url: str) -> Dict[str, Any]:
            """Scrape a URL using Firecrawl"""
            return await self.firecrawl.scrape(
                url, {"formats": ["markdown", "structured_data"], "onlyMainContent": True}
            )

    async def scrape_urls(self, urls: List[str]) -> List[ScrapedData]:
        """Scrape multiple URLs concurrently"""
        tasks = [self.agent.run(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scraped_data = []
        for result in results:
            if not isinstance(result, Exception):
                scraped_data.append(result.data)

        return scraped_data
