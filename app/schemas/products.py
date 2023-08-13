from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Product(BaseModel):
    id: int | float
    product_name: str
    product_key: str
    ch1: str | int | float | None
    ch2: str | int | float | None
    ch3: str | int | float | None
    ch4: str | int | float | None
    ch5: str | int | float | None
    ch6: str | int | float | None
    ch7: str | int | float | None
    ch8: str | int | float | None
    um: str
    quantity: float

    class Config:
        from_attributes = True
