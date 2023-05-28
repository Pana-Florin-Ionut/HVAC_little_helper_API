from passlib.context import CryptContext
from .database import get_db
from . import table_models_required

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_offer_details(offer_name: str, db):
    offer = (
        db.query(table_models_required.Offers)
        .filter(table_models_required.Offers.offer_name == offer_name)
        .first()
    )
    return offer
