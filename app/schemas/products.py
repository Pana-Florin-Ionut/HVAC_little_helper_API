from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from ..schemas.users import UserOut

# from ..schemas.offers import OfferOut


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

    class Config:
        from_attributes = True


class ProductOut(Product):
    id: int
    offer_id: int
    created: datetime
    created_by: int
    owner: UserOut

    class Config:
        from_attributes = True


class OfferOut(BaseModel):
    id: int
    client_key: str | None = None
    company_key: str

    class Config:
        from_attributes = True


class ProductOut2(Product):
    id: int
    offer_id: int
    created: datetime
    created_by: int
    offer: OfferOut

    class Config:
        from_attributes = True
