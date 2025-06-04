import asyncio
from typing import Dict, List, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from ..models.company import SearchQuery
from ..tools.firecrawl_client import FirecrawlClient
from ..tools.web_search import WebSearchTool


class ResearchAgent:
    def __init__(self, api_key: str, tavily_api_key: Optional[str] = None):
        self.model = OpenAIModel("gpt-4-turbo-preview", api_key=api_key)
        self.search_tool = WebSearchTool(api_key=tavily_api_key)
        self.firecrawl = FirecrawlClient()

        self.agent = Agent(
            self.model,
            output_type=List[str],  # Return list of URLs
            system_prompt="""You are a research specialist focused on finding information about retail and warehouse companies.

            Your task is to:
            1. Analyze search results to find the most relevant sources
            2. Prioritize official company websites, industry reports, and credible news
            3. Look for pages mentioning fleet size, warehouses, facilities, employees, stores
            4. Return only the most relevant URLs (max 5) that likely contain the data we need

            Focus on quality over quantity - better to have 3 great sources than 10 mediocre ones.""",
        )

        @self.agent.tool_plain
        async def search_web(query: str) -> List[Dict[str, str]]:
            """Search the web for company information"""
            return await self.search_tool.search_company_info(query)

        @self.agent.tool
        async def filter_relevant_urls(ctx: RunContext[SearchQuery], results: List[Dict[str, str]]) -> List[str]:
            """Filter and rank search results by relevance"""
            relevance_keywords = [
                "truck",
                "fleet",
                "vehicle",
                "transportation",
                "warehouse",
                "distribution",
                "facility",
                "center",
                "employee",
                "workforce",
                "staff",
                "store",
                "location",
                "branch",
                "outlet",
                "annual report",
                "company profile",
                "about us",
            ]
            scored_results = []
            for result in results:
                score = result.get("score", 0.5)
                content = (result.get("title", "") + " " + result.get("snippet", "")).lower()
                keyword_matches = sum(1 for kw in relevance_keywords if kw in content)
                score += keyword_matches * 0.1
                url = result.get("url", "")
                if ctx.deps.company_name.lower().replace(" ", "") in url.lower():
                    score += 0.5
                scored_results.append((score, result["url"]))
            scored_results.sort(key=lambda x: x[0], reverse=True)
            return [url for score, url in scored_results[:5]]

    async def research_company(self, query: SearchQuery) -> List[str]:
        search_queries = [
            f'"{query.company_name}" fleet size trucks vehicles',
            f'"{query.company_name}" warehouse distribution center employees',
            f'"{query.company_name}" number of stores locations facilities',
            f'"{query.company_name}" annual report investor relations',
            f'"{query.company_name}" {query.vertical} company profile about',
        ]
        all_results = []
        for search_query in search_queries:
            try:
                results = await self.search_tool.search_company_info(search_query, max_results=5)
                all_results.extend(results)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Search error for {search_query}: {e}")
                continue
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        if unique_results:
            result = await self.agent.run(unique_results, deps=query)
            return result.data
        return []
