from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


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
