from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
    company_id: Optional[int] = None

