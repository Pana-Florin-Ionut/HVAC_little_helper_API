from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class Product(BaseModel):
    id: int | float
    product_name: str
    ch1: str | None = None
    ch2: str | None = None
    ch3: str | None = None
    ch4: str | None = None
    ch5: str | None = None
    ch6: str | None = None
    ch7: str | None = None
    ch8: str | None = None
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
    created_by: int | str

    class Config:
        orm_mode = True


class OffersCreate(BaseModel):
    client_id: int | None = None
    company_id: int
    project_id: int
    offer_name: str
    offer_key: str
    is_finalized: bool = False
    # created_by: int | str

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
    company_id: int

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    company_id: int
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
    role: Optional[str] = None
