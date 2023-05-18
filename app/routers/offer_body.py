from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, oauth2, table_models_required, table_models_optional, tables
from ..database import engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..database import get_db

router = APIRouter(prefix="/offers/{id}/body", tags=["Offer Body"])


def create_new_offer_table(title):
    table_models_optional.create_offer_table(engine, title)


def get_offer_name(id, db):
    offer = (
        db.query(table_models_required.Offers)
        .filter(table_models_required.Offers.id == id)
        .first()
    )
    offer_name = offer.offer_name
    return offer_name


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_offer_body(id: int, db: Session = Depends(get_db)):
    offer_name = get_offer_name(id, db)
    try:
        table_models_optional.create_offer_table(engine, offer_name)
    except Exception as e:
        print(e)
        return {"message": e}


@router.get("/", response_model=List[schemas.Product])
def get_offer_body(id: int, db: Session = Depends(get_db)):
    offer_name = get_offer_name(id, db)
    response = db.execute(text(tables.get_offer(offer_name)))
    # print(f"response: {response}")
    response_dict = response.mappings().all()
    # print(f"response_dict: {response_dict}")
    return response_dict


# @router.post("/")
# def create_offer(
#     offer: schemas.Offers,
# ):
#     # database_connection.execute_query2(query)
#     try:
#         query = db.make_table(offer.offer_name)
#         db.create_table(query)
#         # return {f"{offer}": f"{offer_name}"}
#         return {"message": f"{offer.offer_name} created"}
#     except Exception as e:
#         print(e)
#         return {"message": e}


# @router.get("/offer/{offer_name}")
# def get_offer(
#     offer_name,
# ):
#     offer = db.get_table(f"SELECT * FROM {offer_name}")
