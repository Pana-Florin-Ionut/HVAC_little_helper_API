from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

import psycopg2
import sqlalchemy
from .. import schemas, oauth2, table_models_required, table_models_optional, tables
from ..database import engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..database import get_db
import logging

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
def create_offer_body(
    offer_name: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # this function should be triggered by the POST offers endpoint
    if user.company_id is None and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    try:
        # check if the offer table exists
        db.execute(text(tables.get_offer(offer_name))).first()
        logging.info(f"{datetime.utcnow()} {offer_name}: Table already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"offer {offer_name} already exists",
        )
    except sqlalchemy.exc.ProgrammingError as e:
        # table not found, proceed to create the table
        table_models_optional.create_offer_table(engine, offer_name)
        logging.info(f"{datetime.utcnow()} {offer_name}: Table Created")
        return {"message": f"{offer_name} created"}
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error",
        )


@router.get("/", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def get_offer_body(
    offer_name: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    if user.company_id is None and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.company_id != get_offer_details(offer_name, db).company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    # try:
    #     # check if the offer table exists
    #     db.execute(text(tables.get_offer(offer_name))).first()
    #     # get the offer details
    #     offer = get_offer_details(offer_name, db)
    #     # get the products
    #     products = db.query(table_models_required.Products).filter(
    #         table_models_required.Products.offer_id == offer.offer_id
    #     ).all()
    #     return products
    # except sqlalchemy.exc.ProgrammingError as e:
    #     if e.orig.pgcode == "42P01":
    #         # check if the offer table exists
    #         logging.error(
    #             f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}"
    #         )
    #         raise HTTPException(:
    try:
        response = db.execute(text(tables.get_offer(offer_name)))
        return response.mappings().all()

    except sqlalchemy.exc.ProgrammingError as e:
        if e.orig.pgcode == "42P01":
            # check if the offer table exists
            logging.error(f"{datetime.utcnow()} {offer_name}: Table not fount + {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"offer {offer_name} does not exist",
            )
        else:
            logging.error(
                f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal Server Error",
            )

    #     logging.error(f"offer {offer_name} does not exist + {e}")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail=f"offer {offer_name} does not exist")
    # except psycopg2.errors.UndefinedTable as e:
    #     logging.error(f"offer {offer_name} does not exist + {e}")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail=f"offer {offer_name} does not exist B")


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
