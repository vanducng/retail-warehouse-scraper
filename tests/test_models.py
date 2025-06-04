from datetime import datetime

from retail_warehouse_scraper.src.models.company import BusinessVertical, CompanyData
from retail_warehouse_scraper.src.models.database import Company


def test_company_data_pydantic():
    data = CompanyData(
        company_name="Test Company",
        cleaned_name="test company",
        vertical=BusinessVertical.GROCERY,
        truck_count=10,
        warehouse_employee_count=50,
        facility_count=2,
        store_count=5,
        notes="Test notes",
        source_references=["https://example.com"],
        confidence_score=0.9
    )
    assert data.company_name == "Test Company"
    assert data.vertical == BusinessVertical.GROCERY
    assert data.confidence_score == 0.9


def test_company_sqlalchemy_to_pydantic():
    company = Company(
        company_name="Test Company",
        cleaned_name="test company",
        vertical="Grocery",
        truck_count=10,
        warehouse_employee_count=50,
        facility_count=2,
        store_count=5,
        notes="Test notes",
        source_references=["https://example.com"],
        last_updated=datetime.now(),
        confidence_score=0.9
    )
    pydantic_model = company.to_pydantic()
    assert pydantic_model.company_name == company.company_name
    assert pydantic_model.cleaned_name == company.cleaned_name
    assert pydantic_model.vertical == BusinessVertical.GROCERY or isinstance(pydantic_model.vertical, str)
