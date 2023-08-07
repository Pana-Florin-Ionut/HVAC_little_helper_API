from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import sqlalchemy as salch

from app.routers.utils import match_user_company
from app.schemas import companies, offers
from .utils import get_offer_details_id, get_product_from_offer
from sqlalchemy import Subquery, select, update, insert, delete, MappingResult
from ..table_models_required import Offers, OffersBody
from .. import oauth2, table_models_required, table_models_optional, tables
from ..schemas import offers as offers_schemas
from ..schemas import products as products_schemas
from ..schemas import users as users_schemas
from ..database import engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..database import get_db
import logging
from .. import user_permissions

router = APIRouter(prefix="/offer", tags=["Offer Body"])


@router.get(
    "/{company_key}/{project_key}/{offer_key}",
    response_model=List[products_schemas.Product],
    status_code=status.HTTP_200_OK,
)
def get_offer_key(
    company_key: str,
    project_key: str,
    offer_key: str,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    subquery = (
        select(Offers.id)
        .where(Offers.company_key == company_key)
        .where(Offers.project_key == project_key)
        .where(Offers.offer_key == offer_key)
        .scalar_subquery()
    )
    match user.role:
        case "application_administrator":
            try:
                query = select(OffersBody).filter(OffersBody.offer_id == subquery)
                response = db.scalars(query).all()
                return response
            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case "admin" | "user":
            if user.company_key != company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            try:
                query = select(OffersBody).filter(OffersBody.offer_id == subquery)
                response = db.scalars(query).all()
                return response
            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case "custom":
            if user.company_key != company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            if user_permissions.can_view_offer(user.id, db) == False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            try:
                query = select(OffersBody).filter(OffersBody.offer_id == subquery)
                response = db.scalars(query).all()
                return response
            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )


@router.get(
    "/{offer_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[products_schemas.Product],
)
def get_offer_details(
    offer_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    """
    Get a list of products from same offer (offer_id)
    """
    query = select(OffersBody).filter(OffersBody.offer_id == offer_id)
    match user.id:
        case "application_administrator":
            try:
                response = db.scalars(query).all()
                return response
            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case "admin" | "user" | "worker":
            try:
                offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)
                if user.company_key != offer.company_key:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                    )
                response = db.scalars(query).all()
                return response
            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case "custom":
            offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)

            if user.company_key != offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            if user_permissions.can_view_offer(user.id, db) == False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            try:
                response = db.scalars(query).all()
                return response
            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_offer_table(
    offer_name: str,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    pass


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)
    if user.company_key is None or user.role != "application_administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    elif user.company_key != offer.company_key and user.role not in [
        "admin",
        "manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        # db.execute(text(tables.delete_offer(offer_id)))
        db.delete(offer)
        db.commit()
        logging.info(f"{datetime.utcnow()} {offer.offer_name}: Table Deleted")
        return {"message": f"{offer.offer_name} deleted"}
    except salch.exc.ProgrammingError as e:
        if e.orig.pgcode == "42P01":
            # check if the offer table exists
            logging.error(
                f"{datetime.utcnow()} {offer.offer_name}: Table not found + {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Offer with id = {offer_id} does not exist",
            )
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {offer_id}: Internal Server Error + {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error",
        )


@router.put(
    "/{product_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=offers.OffersRetrieve,
)
def update_offer(
    offer_id: int,
    new_product_name: str,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    product: offers.Product = get_product_from_offer(offer_id, db)
    offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)
    if user.company_key is None or user.role != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.company_key != product.company_key and user.role not in [
        "admin",
        "manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        offer.offer_name = new_product_name
        db.commit()
        db.refresh(offer)

        logging.info(
            f"{datetime.utcnow()} {offer_id} -> {new_product_name}: Table Updated"
        )
        return offer
    except salch.exc.ProgrammingError as e:
        if e.orig.pgcode == "42P01":
            # check if the offer table exists
            logging.error(f"{datetime.utcnow()} {offer_id}: Table not found + {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {offer_id}: Internal Server Error + {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error",
        )


@router.post("/add_product", status_code=status.HTTP_202_ACCEPTED)
def add_product_to_offer(
    offer_name: str,
    product: products_schemas.Product,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
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
    except salch.exc.ProgrammingError as e:
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
