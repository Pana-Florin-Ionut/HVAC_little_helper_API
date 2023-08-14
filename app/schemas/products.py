from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Product(BaseModel):
    product_name: str
    product_key: str
    ch_1: str | int | float | None = None
    ch_2: str | int | float | None = None
    ch_3: str | int | float | None = None
    ch_4: str | int | float | None = None
    ch_5: str | int | float | None = None
    ch_6: str | int | float | None = None
    ch_7: str | int | float | None = None
    ch_8: str | int | float | None = None
    um: str
    quantity: float
    observations: str | None = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    id: int | float
    product: Product


class ProductOut(Product):
    id: int
    offer_id: int
    created: datetime
    created_by: int
