from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from .products import Product


class Offer(BaseModel):
    products: list[Product] | None = None


class Offers(BaseModel):
    id: int | None = None
    client_id: int | None = None
    company_id: int
    project_id: int
    offer_name: str
    offer_key: str
    is_finalized: bool
    timestamp: datetime
    offer_body: List[Offer | None]

    class Config:
        orm_mode = True


class OffersRetrieve(BaseModel):
    id: int
    client_id: int | None = None
    company_id: int
    project_id: int
    offer_name: str
    offer_key: str
    is_finalized: bool
    created: datetime
    created_by: int

    class Config:
        orm_mode = True


class OffersCreate(BaseModel):
    client_id: int | None = None
    company_id: int
    project_id: int
    offer_name: str
    offer_key: str
    is_finalized: bool = False

    class Config:
        orm_mode = True
