import asyncio
from functools import partial
from typing import Any, Dict, Optional

import httpx
from firecrawl import FirecrawlApp


class FirecrawlClient:
    def __init__(self, api_key: Optional[str] = None):
        self.app = FirecrawlApp(api_key=api_key) if api_key else None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def scrape(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape a URL using Firecrawl"""
        if self.app:
            loop = asyncio.get_event_loop()
            scrape_func = partial(self.app.scrape_url, url, params=params)
            result = await loop.run_in_executor(None, scrape_func)
            return result
        else:
            response = await self.client.get(url)
            return {"content": response.text, "url": url, "status_code": response.status_code}

    async def search(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search using Firecrawl"""
        if self.app:
            loop = asyncio.get_event_loop()
            search_func = partial(self.app.search, query, params=params)
            result = await loop.run_in_executor(None, search_func)
            return result
        else:
            return {"results": [], "query": query}
