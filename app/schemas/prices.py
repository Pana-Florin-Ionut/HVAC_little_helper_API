from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from app.schemas.companies import CompanyOut
from app.schemas.projects import ProjectOut, ProjectSingleOut

from app.schemas.users import UserOut
from .products import Product, ProductOut2


class PricesOut(BaseModel):
    id: int
    offering_company: int
    offer_product_id: int
    price: float

    # currency: str #Maybe latter
    class Config:
        from_attributes = True


class ProductWithPrices(BaseModel):
    id: int
    product: ProductOut2
    offering_company: int
    offer_product_id: int
    price: float

    class Config:
        from_attributes = True
