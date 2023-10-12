from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Company(BaseModel):
    id: int
    company_name: str
    company_key: str

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    company_name: str
    company_key: str

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    company_name: str

    class Config:
        from_attributes = True


class CompanyOut(BaseModel):
    id: int
    company_name: str
    company_key: str
    created: datetime

    class Config:
        from_attributes = True
