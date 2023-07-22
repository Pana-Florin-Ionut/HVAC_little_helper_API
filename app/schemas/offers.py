from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from app.schemas.companies import CompanyOut
from app.schemas.projects import ProjectOut, ProjectSingleOut

from app.schemas.users import UserOut
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
    owner: UserOut
    company: CompanyOut
    client: CompanyOut
    project: ProjectSingleOut

    class Config:
        orm_mode = True


class OffersCreateUser(BaseModel):
    client_id: int | None = None
    project_id: int
    offer_name: str
    offer_key: str

    class Config:
        orm_mode = True

class OffersCreateAdmin(OffersCreateUser):
    company_id: int