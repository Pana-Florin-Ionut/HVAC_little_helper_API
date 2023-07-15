from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from .companies import CompanyOut
from .users import UserOut







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

class ProjectSingleOut(BaseModel):
    id: int
    company_id: int
    project_name: str
    project_key: str
    created_by: int
    created: datetime

    class Config:
        orm_mode = True