import asyncio
import os
from functools import partial
from typing import Dict, List, Optional

import httpx
from tavily import TavilyClient


class WebSearchTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def search_company_info(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Search for company information using Tavily API"""
        if not self.client:
            raise ValueError("Tavily API key not provided")

        try:
            # Tavily search is synchronous, so we run it in executor
            loop = asyncio.get_event_loop()
            search_func = partial(
                self.client.search,
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=True,
            )

            response = await loop.run_in_executor(None, search_func)

            results = []
            for result in response.get("results", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "raw_content": result.get("raw_content", ""),
                        "score": result.get("score", 0.0),
                    }
                )

            # Include AI-generated answer if available
            if response.get("answer"):
                results.insert(
                    0,
                    {
                        "title": "AI Summary",
                        "url": query,
                        "snippet": response["answer"],
                        "raw_content": response["answer"],
                        "score": 1.0,
                    },
                )

            return results

        except Exception as e:
            print(f"Tavily search error: {e}")
            # Fallback to free alternative (DuckDuckGo)
            return await self._fallback_search(query, max_results)

    async def _fallback_search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Fallback search using DuckDuckGo HTML API (free, no key required)"""
        try:
            from bs4 import BeautifulSoup

            # DuckDuckGo HTML search
            params = {"q": query, "t": "h_", "ia": "web"}

            response = await self.http_client.get(
                "https://html.duckduckgo.com/html/",
                params=params,
                headers={"User-Agent": "Mozilla/5.0 (compatible; AI-Agent/1.0)"},
            )

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for result in soup.find_all("div", class_="result")[:max_results]:
                title_elem = result.find("a", class_="result__a")
                snippet_elem = result.find("a", class_="result__snippet")

                if title_elem:
                    results.append(
                        {
                            "title": title_elem.get_text(strip=True),
                            "url": title_elem.get("href", ""),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                            "raw_content": "",
                            "score": 0.5,
                        }
                    )

            return results

        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
