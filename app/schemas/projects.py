from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from .companies import CompanyOut
from .users import UserOut


class Project(BaseModel):
    id: int
    company_key: str
    project_name: str
    project_key: str
    created_by: UserOut

    class Config:
        from_attributes = True


class ProjectCreateAdmin(BaseModel):
    company_key: str
    project_name: str
    project_key: str

    class Config:
        from_attributes = True


class ProjectUpdateAdmin(BaseModel):
    project_name: str

    class Config:
        from_attributes = True


class ProjectCreateUser(BaseModel):
    project_name: str
    project_key: str

    class Config:
        from_attributes = True


class ProjectSellersOut(BaseModel):
    id: int
    company_key: str
    project_name: str
    project_key: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    company_key: str
    project_name: str
    project_key: str
    created_by: int
    created: datetime
    owner: UserOut
    company: CompanyOut

    class Config:
        from_attributes = True


class ProjectSingleOut(BaseModel):
    id: int
    company_key: str
    project_name: str
    project_key: str
    created_by: int
    created: datetime

    class Config:
        from_attributes = True
