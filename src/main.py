import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from .agents.analysis_agent import AnalysisAgent
from .agents.research_agent import ResearchAgent
from .agents.scraping_agent import ScrapingAgent
from .database.connection import get_db_engine, get_db_session
from .models.company import BusinessVertical, CompanyData, SearchQuery
from .models.database import Base, Company

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetailWarehouseScraper:
    def __init__(self, openai_api_key: str, firecrawl_api_key: str):
        self.research_agent = ResearchAgent(openai_api_key)
        self.scraping_agent = ScrapingAgent(openai_api_key, firecrawl_api_key)
        self.analysis_agent = AnalysisAgent(openai_api_key)

        # Initialize database
        self.engine = get_db_engine()
        Base.metadata.create_all(self.engine)

    async def process_company(self, company_name: str, vertical: str, session: Session) -> Optional[CompanyData]:
        """Process a single company"""
        try:
            # Check if we have recent data
            existing = session.query(Company).filter_by(company_name=company_name).first()
            if existing and existing.last_updated > datetime.now() - timedelta(days=30):
                logger.info(f"Using cached data for {company_name}")
                return existing.to_pydantic()

            logger.info(f"Processing {company_name}")

            # Create search query
            query = SearchQuery(company_name=company_name, vertical=BusinessVertical(vertical))

            # Research phase
            urls = await self.research_agent.research_company(query)
            if not urls:
                logger.warning(f"No URLs found for {company_name}")
                return None

            # Scraping phase
            scraped_data = await self.scraping_agent.scrape_urls(urls[:3])  # Limit to top 3 URLs
            if not scraped_data:
                logger.warning(f"No data scraped for {company_name}")
                return None

            # Analysis phase
            company_data = await self.analysis_agent.analyze_company_data(query, scraped_data)

            # Save to database
            if existing:
                # Update existing record
                for key, value in company_data.model_dump(exclude={"last_updated"}).items():
                    setattr(existing, key, value)
                existing.last_updated = datetime.now()
            else:
                # Create new record
                new_company = Company(**company_data.model_dump())
                session.add(new_company)

            session.commit()
            logger.info(f"Successfully processed {company_name}")
            return company_data

        except Exception as e:
            logger.error(f"Error processing {company_name}: {str(e)}")
            session.rollback()
            return None

    async def process_csv(self, input_path: Path, output_path: Path):
        """Process companies from CSV file"""
        # Read input CSV
        df = pd.read_csv(input_path)

        # Process companies in batches
        batch_size = 5
        results = []

        with get_db_session(self.engine) as session:
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i : i + batch_size]
                tasks = []

                for _, row in batch.iterrows():
                    company_name = row["Company Name"]
                    vertical = row.get("Vertical", "General")
                    tasks.append(self.process_company(company_name, vertical, session))

                batch_results = await asyncio.gather(*tasks)
                results.extend([r for r in batch_results if r])

                # Save intermediate results
                if results:
                    self._save_results(results, output_path)

                # Rate limiting
                await asyncio.sleep(2)

        logger.info(f"Processed {len(results)} companies successfully")
        return results

    def _save_results(self, results: List[CompanyData], output_path: Path):
        """Save results to CSV"""
        data = []
        for company in results:
            data.append(
                {
                    "Company Name": company.company_name,
                    "Cleaned Name": company.cleaned_name,
                    "Vertical": company.vertical,
                    "Truck Count": company.truck_count,
                    "Warehouse Employee Count": company.warehouse_employee_count,
                    "Facility Count": company.facility_count,
                    "Store Count": company.store_count,
                    "Notes": company.notes,
                    "Source References": ", ".join([str(url) for url in company.source_references]),
                    "Last Updated": company.last_updated.isoformat(),
                    "Confidence Score": company.confidence_score,
                }
            )

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(data)} records to {output_path}")


async def main():
    """Main entry point"""
    import os

    from dotenv import load_dotenv

    load_dotenv()

    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

    if not openai_api_key or not firecrawl_api_key:
        raise ValueError("Missing required API keys. Set OPENAI_API_KEY and FIRECRAWL_API_KEY in .env file")

    # Initialize scraper
    scraper = RetailWarehouseScraper(openai_api_key, firecrawl_api_key)

    # Process companies
    input_path = Path("data/input/retail_and_warehouse_research.csv")
    output_path = Path("data/output/enriched_companies.csv")

    await scraper.process_csv(input_path, output_path)


if __name__ == "__main__":
    asyncio.run(main())
