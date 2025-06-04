from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class BusinessVertical(str, Enum):
    GROCERY = "Grocery"
    BEVERAGE = "Beverage"
    MANUFACTURING = "Manufacturing"
    WAREHOUSE = "Warehouse"
    WHOLESALE_RETAIL = "Wholesale/Retail"
    FOODSERVICE = "Foodservice"
    PETROLEUM_CHEMICAL = "Petroleum/Chemical"
    AGRICULTURE_FOOD = "Agriculture & Food Processing"
    WASTE_MANAGEMENT = "Waste Management"
    CONSTRUCTION = "Construction"
    LANDSCAPING = "Landscaping"
    GENERAL = "General"
    PAPER_OFFICE = "Paper & Office Products"


class CompanyData(BaseModel):
    """Structured company data model"""

    company_name: str = Field(..., description="Official company name")
    cleaned_name: str = Field(..., description="Cleaned/standardized company name")
    vertical: BusinessVertical = Field(..., description="Business vertical/industry")
    truck_count: Optional[int] = Field(None, description="Number of trucks owned/operated")
    warehouse_employee_count: Optional[int] = Field(None, description="Number of warehouse employees")
    facility_count: Optional[int] = Field(None, description="Number of facilities/warehouses")
    store_count: Optional[int] = Field(None, description="Number of retail stores")
    notes: Optional[str] = Field(None, description="Additional relevant information")
    source_references: List[HttpUrl] = Field(default_factory=list, description="Source URLs")
    last_updated: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Data confidence score")


class SearchQuery(BaseModel):
    """Search query model"""

    company_name: str
    vertical: BusinessVertical
    additional_context: Optional[str] = None


class ScrapedData(BaseModel):
    """Raw scraped data model"""

    url: HttpUrl
    content: str
    extracted_data: dict
    scrape_timestamp: datetime = Field(default_factory=datetime.now)
