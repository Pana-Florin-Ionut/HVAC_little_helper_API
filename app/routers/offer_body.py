from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from . import utils
from app.schemas import companies, offer_body, offers, products
from .utils import get_offer_details_id, get_product_from_offer
from sqlalchemy import Subquery, select, update, insert, delete, MappingResult
from ..table_models_required import Offers, OffersBody
from .. import oauth2, table_models_required, table_models_optional, tables
from ..schemas import offers as offers_schemas
from ..schemas import products as products_schemas
from ..schemas import users as users_schemas
from sqlalchemy.orm import Session
from ..database import get_db
from ..roles import Roles
import logging
from .. import user_permissions

router = APIRouter(prefix="/offer", tags=["Offer Body"])


@router.get(
    "/{company_key}/{project_key}/{offer_key}",
    response_model=list[products_schemas.ProductOut],
    status_code=status.HTTP_200_OK,
)
def get_offer_details_keys(
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
        case Roles.app_admin:
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
        case Roles.admin | Roles.user:
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
        case Roles.custom:
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
    response_model=list[products.ProductOut],
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
    print(f"Query: {query}")
    match user.role:
        case Roles.app_admin:
            try:
                response = db.scalars(query).all()
                return response

            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case Roles.admin | Roles.user | Roles.worker:
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
        case Roles.custom:
            offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)
            if user_permissions.can_view_offer(user.id, db) == False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            if user.company_key != offer.company_key:
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


@router.post(
    "/{offer_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=products.ProductOut,
)
def add_product_to_offer(
    offer_id: int,
    product: products.Product,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case Roles.app_admin:
            try:
                query = (
                    insert(OffersBody)
                    .values(
                        **product.model_dump(), offer_id=offer_id, created_by=user.id
                    )
                    .returning(OffersBody)
                )
                response = db.scalars(query)
                db.commit()
                logging.info(
                    f"{datetime.utcnow()} product: {product} added to offer with id: {offer_id}"
                )
                return response.first()
            except Exception as e:
                logging.error(
                    f"{datetime.utcnow()} {offer_id}: Internal Server Error + {e}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal Server Error",
                )
        case Roles.admin | Roles.user:
            offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)
            if user.company_key != offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not your offer"
                )
            try:
                query = (
                    insert(OffersBody)
                    .values(
                        **product.model_dump(), offer_id=offer_id, created_by=user.id
                    )
                    .returning(OffersBody)
                )
                response = db.scalars(query)
                db.commit()
                logging.info(
                    f"{datetime.utcnow()} product: {product} added to offer with id: {offer_id}"
                )
                return response.first()
            except Exception as e:
                logging.error(
                    f"{datetime.utcnow()} {offer_id}: Internal Server Error + {e}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal Server Error",
                )
        case Roles.custom:
            offer: offers.OffersRetrieve = utils.get_offer_details_id(offer_id, db)
            if user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            if user.company_key != offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not your offer"
                )
            try:
                query = (
                    insert(OffersBody)
                    .values(
                        **product.model_dump(), offer_id=offer_id, created_by=user.id
                    )
                    .returning(OffersBody)
                )
                response = db.scalars(query)
                db.commit()
                logging.info(
                    f"{datetime.utcnow()} product: {product} added to offer with id: {offer_id}"
                )
                return response.first()
            except Exception as e:
                logging.error(
                    f"{datetime.utcnow()} {offer_id}: Internal Server Error + {e}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal Server Error",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )


@router.delete("/{offer_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
# need to remove offer_id as you can get it from the product schema
def delete_offer(
    product_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    offer: offers.OffersRetrieve = get_offer_details_id(offer_id, db)
    # print(user.company_key)
    # print(user.role)
    match user.role:
        case Roles.app_admin:
            db.delete(table_models_required.OffersBody, id=product_id)
            db.commit()
            logging.info(f"{datetime.utcnow()} {offer.offer_name}: Table Deleted")
            return {
                "message": f"Product {product_id} was deleted from {offer.offer_name}"
            }
        case Roles.admin | "manager":
            if user.company_key != offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not your offer"
                )
            db.delete(table_models_required.OffersBody, id=product_id)
            db.commit()
            logging.info(
                f"{datetime.utcnow()} Product {product_id} was deleted from {offer.offer_name}"
            )
            return {
                "message": f"Product {product_id} was deleted from {offer.offer_name}"
            }
        case Roles.custom:
            if not user_permissions.can_create_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            db.delete(table_models_required.OffersBody, id=product_id)
            db.commit()
            logging.info(
                f"{datetime.utcnow()} Product {product_id} was deleted from {offer.offer_name}"
            )
            return {
                "message": f"Product {product_id} was deleted from {offer.offer_name}"
            }
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )


@router.put(
    "/{product_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=products.ProductOut,
)
def update_offer(
    product_update: products.Product,
    product_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    product: products.ProductOut = (
        db.query(table_models_required.OffersBody)
        .filter(table_models_required.OffersBody.id == product_id)
        .first()
    )
    # offer: offers.OffersRetrieve = db.get(table_models_required.Offers, product.offer_id)
    match user.role:
        case Roles.app_admin:
            try:
                # try use the product from above
                query = (
                    update(table_models_required.OffersBody)
                    .where(table_models_required.OffersBody.id == product_id)
                    .values(**product_update.model_dump())
                    .returning(OffersBody)
                )
                response = db.scalars(query).first()
                db.commit()
                # logging.info(f"{datetime.utcnow()} {offer.offer_name}: Table Updated")
                return response
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )
