from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class Product(BaseModel):
    id: int | float
    product_name: str
    ch1: str | int | float | None
    ch2: str | int | float | None
    ch3: str | int | float | None
    ch4: str | int | float | None
    ch5: str | int | float | None
    ch6: str | int | float | None
    ch7: str | int | float | None
    ch8: str | int | float | None
    UM: str
    quantity: float


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
    timestamp: datetime
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


class User(BaseModel):
    id: int
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_id: int | None = None

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    company_id: int | None = None
    role: str | None = None
    created: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
    company_id: Optional[int] = None


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

class Project(BaseModel):
    id: int
    company_id: int
    project_name: str
    project_key: str
    created_by: UserOut

    class Config:
        orm_mode = True

class ProjectCreateAdmin(BaseModel):
    company_id: int
    project_name: str
    project_key: str

    class Config:
        orm_mode = True

class ProjectUpdateAdmin(BaseModel):
    project_name: str

    class Config:
        orm_mode = True
        
class ProjectCreateUser(BaseModel):
    project_name: str
    project_key: str

    class Config:
        orm_mode = True

class ProjectOut(BaseModel):
    id: int
    company_id: int
    project_name: str
    project_key: str
    created_by: int
    created: datetime
    owner: UserOut
    company: CompanyOut

    class Config:
        orm_mode = True