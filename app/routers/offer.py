from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..utils import get_offer_details
import sqlalchemy
from .. import schemas, oauth2, table_models_required, table_models_optional, tables
from ..database import engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..database import get_db
import logging
from .. import user_permissions

router = APIRouter(prefix="/offer/{offer_name}", tags=["Offer Body"])


def create_new_offer_table(offer_name):
    table_models_optional.create_offer_table(engine, offer_name)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_offer_table(
    offer_name: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # this function should be triggered by the POST offers endpoint
    # print(user)
    print(offer_name)
    if user_permissions.can_create_offer(user.id, db):
        try:
            table_models_optional.create_offer_table(engine, offer_name)
            return {"message": f"{offer_name} created"}
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"offer {offer_name} already exists",
            )


@router.get("/", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def get_offer(
    offer_name: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    if user_permissions.can_view_offer(user.id, db):
        try:
            response = db.execute(text(tables.get_offer(offer_name)))
            return response.mappings().all()
        except sqlalchemy.exc.ProgrammingError as e:
            if e.orig.pgcode == "42P01":
                # check if the offer table exists
                logging.error(
                    f"{datetime.utcnow()} {offer_name}: Table not found + {e}"
                )
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
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(
    offer_name: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    if user.company_id is None or user.role != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.company_id != get_offer_details(offer_name, db).company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        db.execute(text(tables.delete_offer(offer_name)))
        logging.info(f"{datetime.utcnow()} {offer_name}: Table Deleted")
        return {"message": f"{offer_name} deleted"}
    except sqlalchemy.exc.ProgrammingError as e:
        if e.orig.pgcode == "42P01":
            # check if the offer table exists
            logging.error(f"{datetime.utcnow()} {offer_name}: Table not found + {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Offer {offer_name} does not exist",
            )
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error",
        )


@router.put("/", status_code=status.HTTP_202_ACCEPTED)
def update_offer(
    offer_name: str,
    new_offer_name: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    if user.company_id is None or user.role != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.company_id != get_offer_details(offer_name, db).company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        db.execute(text(tables.modify_offer(offer_name, new_offer_name)))

        logging.info(
            f"{datetime.utcnow()} {offer_name} -> {new_offer_name}: Table Updated"
        )
        return {"message": f"{offer_name} updated"}
    except sqlalchemy.exc.ProgrammingError as e:
        if e.orig.pgcode == "42P01":
            # check if the offer table exists
            logging.error(f"{datetime.utcnow()} {offer_name}: Table not found + {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error",
        )


@router.post("/add_product", status_code=status.HTTP_202_ACCEPTED)
def add_product_to_offer(
    offer_name: str,
    product: schemas.Product,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    print(product)
    if user.company_id is None or user.role != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.company_id != get_offer_details(offer_name, db).company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.role not in ["admin", "manager", "worker"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        db.execute(text(tables.add_product_to_offer(offer_name, **product)))
        logging.info(f"{datetime.utcnow()} {offer_name}: Product Added")
        return {"message": f"{offer_name} updated"}
    except sqlalchemy.exc.ProgrammingError as e:
        if e.orig.pgcode == "42P01":
            # check if the offer table exists
            logging.error(f"{datetime.utcnow()} {offer_name}: Table not found + {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error",
        )
