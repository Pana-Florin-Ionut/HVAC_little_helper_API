from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from app.schemas.companies import CompanyOut
from app.schemas.projects import ProjectOut, ProjectSingleOut

from app.schemas.users import UserOut
from .products import Product


class Offer(BaseModel):
    products: list[Product] | None = None

    class Config:
        from_attributes = True


class Offers(BaseModel):
    id: int | None = None
    client_key: str | None = None
    company_key: str
    project_key: str
    offer_name: str
    offer_key: str
    is_finalized: bool
    timestamp: datetime
    offer_body: List[Offer | None]

    class Config:
        from_attributes = True


class OffersRetrieve(BaseModel):
    id: int
    client_key: str | None = None
    company_key: str
    project_key: str
    offer_name: str
    offer_key: str
    is_finalized: bool
    created: datetime
    created_by: int
    owner: UserOut
    company: CompanyOut
    client: CompanyOut
    project: ProjectSingleOut

    class Config:
        from_attributes = True


class OffersCreateUser(BaseModel):
    client_key: str | None = None
    project_id: int
    project_key: str | None = None
    offer_name: str
    offer_key: str

    class Config:
        from_attributes = True


class OffersCreateAdmin(OffersCreateUser):
    company_key: str


class OffersUpdate(BaseModel):
    offer_name: str
    is_finalized: bool

    class Config:
        from_attributes = True
