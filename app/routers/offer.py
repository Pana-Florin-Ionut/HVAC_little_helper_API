from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

import psycopg2
import sqlalchemy
from .. import schemas, oauth2, table_models_required, table_models_optional, tables
from ..database import engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..database import get_db

router = APIRouter(prefix="/offer/{offer_name}", tags=["Offer Body"])


def create_new_offer_table(offer_name):
    table_models_optional.create_offer_table(engine, offer_name)


def get_offer_details(offer_name, db):
    offer = (
        db.query(table_models_required.Offers)
        .filter(table_models_required.Offers.offer_name == offer_name)
        .first()
    )
    return offer


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_offer_body(offer_name: str, db: Session = Depends(get_db)):
    
    try:
        #check if the offer table exists
        db.execute(text(tables.get_offer(offer_name))).first() 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"offer {offer_name} already exists") 
    except sqlalchemy.exc.ProgrammingError as e:
        #if the table is not found
        print(e)
        pass
    
    table_models_optional.create_offer_table(engine, offer_name)
    return {"message": f"{offer_name} created"}       



@router.get("/", response_model=List[schemas.Product])
def get_offer_body(offer_name: str,  db: Session = Depends(get_db)):
    response = db.execute(text(tables.get_offer(offer_name)))
    response_dict = response.mappings().all()
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
