import os
from pathlib import Path

import click
from dotenv import load_dotenv

from .main import RetailWarehouseScraper

load_dotenv()


@click.group()
def cli():
    """Retail and Warehouse Business Prospect Scraper"""
    pass


@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), required=True, help="Input CSV file")
@click.option("--output", "-o", type=click.Path(), default="data/output/enriched_companies.csv", help="Output CSV file")
@click.option("--batch-size", "-b", type=int, default=5, help="Batch size for processing")
async def scrape(input, output, batch_size):
    """Scrape company information from web"""
    scraper = RetailWarehouseScraper(
        openai_api_key=os.getenv("OPENAI_API_KEY"), firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY")
    )

    await scraper.process_csv(Path(input), Path(output))


@cli.command()
@click.option("--company", "-c", type=str, required=True, help="Company name to search")
@click.option("--vertical", "-v", type=str, default="General", help="Business vertical")
async def search(company, vertical):
    """Search for a single company"""
    from .database.connection import get_db_engine, get_db_session

    scraper = RetailWarehouseScraper(
        openai_api_key=os.getenv("OPENAI_API_KEY"), firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY")
    )

    engine = get_db_engine()
    with get_db_session(engine) as session:
        result = await scraper.process_company(company, vertical, session)
        if result:
            click.echo(result.model_dump_json(indent=2))
        else:
            click.echo(f"No data found for {company}")


if __name__ == "__main__":
    cli()
