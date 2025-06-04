from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    company_name = Column(String, unique=True, nullable=False)
    cleaned_name = Column(String, nullable=False)
    vertical = Column(String, nullable=False)
    truck_count = Column(Integer, nullable=True)
    warehouse_employee_count = Column(Integer, nullable=True)
    facility_count = Column(Integer, nullable=True)
    store_count = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    source_references = Column(JSON, default=list)
    last_updated = Column(DateTime, default=datetime.now)
    confidence_score = Column(Float, default=0.0)

    def to_pydantic(self):
        """Convert SQLAlchemy model to Pydantic model"""
        from .company import CompanyData

        return CompanyData(
            company_name=self.company_name,
            cleaned_name=self.cleaned_name,
            vertical=self.vertical,
            truck_count=self.truck_count,
            warehouse_employee_count=self.warehouse_employee_count,
            facility_count=self.facility_count,
            store_count=self.store_count,
            notes=self.notes,
            source_references=self.source_references or [],
            last_updated=self.last_updated,
            confidence_score=self.confidence_score,
        )
