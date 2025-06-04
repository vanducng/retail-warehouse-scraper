import re
from typing import List, Optional

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from ..models.company import CompanyData, ScrapedData, SearchQuery


class AnalysisAgent:
    def __init__(self, api_key: str):
        self.model = OpenAIModel("gpt-4-turbo-preview", api_key=api_key)

        self.agent = Agent(
            self.model,
            output_type=CompanyData,
            system_prompt="""You are a data analysis expert specializing in extracting and validating company information.

            Given scraped web data, extract and validate:
            1. Truck/Fleet counts - look for specific numbers mentioned with trucks, fleet, vehicles
            2. Warehouse employee counts - focus on distribution center or warehouse-specific employee numbers
            3. Facility counts - warehouses, distribution centers, fulfillment centers
            4. Store counts - retail locations, stores, branches

            Rules:
            - Only use specific numbers found in the text, don't estimate
            - If a range is given (e.g., '200-300 trucks'), use the midpoint
            - Assign confidence scores: 1.0 for exact numbers, 0.8 for ranges, 0.6 for estimates
            - Include source URLs for each data point
            - Add relevant notes about data quality or additional context""",
        )

        @self.agent.tool_plain
        def extract_numbers(text: str, keywords: List[str]) -> Optional[int]:
            """Extract numbers associated with specific keywords"""
            for keyword in keywords:
                # Pattern to find numbers near keywords
                pattern = rf"(\d+(?:,\d+)*)\s*{keyword}"
                match = re.search(pattern, text.lower())
                if match:
                    return int(match.group(1).replace(",", ""))
            return None

    async def analyze_company_data(self, query: SearchQuery, scraped_data: List[ScrapedData]) -> CompanyData:
        """Analyze scraped data and return structured company information"""
        # Combine all scraped content
        combined_content = "\n\n".join([f"Source: {data.url}\n{data.content}" for data in scraped_data])

        # Run analysis
        result = await self.agent.run(
            combined_content,
            deps={
                "company_name": query.company_name,
                "vertical": query.vertical,
                "urls": [str(data.url) for data in scraped_data],
            },
        )

        return result.data
