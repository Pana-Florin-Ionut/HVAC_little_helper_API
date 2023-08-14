from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from app.schemas.companies import CompanyOut
from app.schemas.projects import ProjectOut, ProjectSingleOut

from app.schemas.users import UserOut
from .products import Product


class OfferBody(BaseModel):
    product: Product
    observations: str

    class Config:
        from_attributes = True
