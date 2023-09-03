from datetime import datetime
from typing import List, Optional
from enum import Enum
from ..schemas.companies import Company

from pydantic import BaseModel, EmailStr


class AccessRoles(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"
    guest = "guest"
    worker = "worker"
    custom = "custom"
    test = "test"


class Roles(str, Enum):
    app_admin = "application_administrator"
    admin = "admin"
    manager = "manager"
    user = "user"
    guest = "guest"
    worker = "worker"
    custom = "custom"
    test = "test"


class User(BaseModel):
    id: int
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_key: str | None = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    company_key: str | None = None
    role: Roles | None = None
    created: datetime
    company: Company | None = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserUpdateBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        from_attributes = True


class UserUpdate(UserUpdateBase):
    role: AccessRoles | None = None

    class Config:
        from_attributes = True


class UserUpdateAdministrator(UserUpdateBase):
    role: Roles | None = None
    company_key: str | None = None

    class Config:
        from_attributes = True
