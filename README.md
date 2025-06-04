# Retail Warehouse Scraper

AI agent for scraping retail and warehouse business prospect information.

## Architecture

- **Agents**: Modular agents for research, scraping, and analysis
- **Database**: SQLite with SQLAlchemy ORM
- **Data Models**: Pydantic for structured validation
- **Web Scraping**: Firecrawl API (with fallback)
- **LLM**: OpenAI GPT-4 (or Anthropic Claude)
- **Async**: Efficient batch processing

**Workflow:**
1. **Research**: Find relevant URLs for company info
2. **Scrape**: Extract structured data from URLs
3. **Analyze**: Validate and structure the data
4. **Save**: Store in database and export to CSV

## Quick Start Guide

```bash
# 1. Clone and setup
git clone <your-repo>
cd retail_warehouse_scraper

# 2. Install UV and setup environment
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
uv pip install -e ".[dev]"

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the scraper
uv run python -m src.cli scrape -i data/input/retail_and_warehouse_research.csv

# 6. Or search a single company
uv run python -m src.cli search -c "Walmart" -v "Wholesale/Retail"
```

## Example CLI Usage

- Batch scrape: `uv run python -m src.cli scrape -i data/input/retail_and_warehouse_research.csv`
- Single company: `uv run python -m src.cli search -c "Walmart" -v "Wholesale/Retail"`

## Testing

```bash
uv run pytest
```

- Tests are in the `tests/` directory
- Includes model, agent, and tool tests (with mocks)

## Extending

- Add new companies to the input CSV
- Add new agent logic or business verticals in `src/models/company.py`
- Add new scraping or analysis tools in `src/tools/`

## Features
- Structured data models with Pydantic
- Async processing for efficiency
- Database caching to avoid redundant scraping
- CLI interface for easy usage
- Proper logging and monitoring
- Type safety throughout the codebase
