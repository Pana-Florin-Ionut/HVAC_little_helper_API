from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Offer(BaseModel):    
    id: int | float
    product_name: str
    ch1: str
    ch2: str
    ch3: str
    ch4: str
    ch5: str
    ch6: str
    ch7: str
    ch8: str
    UM: str
    quantity: float



class Offers(BaseModel):
    id: int | None =  None
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
    company_id: int
    project_id: int
    offer_name: str
    offer_key: str
    is_finalized: bool
    timestamp: datetime

    class Config:
        orm_mode = True

class OffersCreate(BaseModel):
    company_id: int
    project_id: int
    offer_name: str
    offer_key: str
    is_finalized: bool = False
    # created_by: str = "admin"

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

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created: datetime

    class Config:
        orm_mode = True