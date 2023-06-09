from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Company(BaseModel):
    id: int
    company_name: str
    company_key: str

    class Config:
        orm_mode = True


class CompanyCreate(BaseModel):
    company_name: str
    company_key: str

    class Config:
        orm_mode = True


class CompanyOut(BaseModel):
    id: int
    company_name: str
    company_key: str
    created: datetime

    class Config:
        orm_mode = True
