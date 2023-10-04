from pydantic import BaseModel
from . import companies, offers


class CompanyConnectionsIn(BaseModel):
    friend_id: int
    offer_id: int

    class Config:
        from_attributes = True


class CompanyConnectionsFull(BaseModel):
    id: int
    company: companies.Company
    friend: companies.Company
    offer: offers.OffersSellersOutLite

    class Config:
        from_attributes = True


class CompanyConnectionsShort(BaseModel):
    id: int
    company_id: int
    offer_id: int
    friend_id: int

    class Config:
        from_attributes = True
