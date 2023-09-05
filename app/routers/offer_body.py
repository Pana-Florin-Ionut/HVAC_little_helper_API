from datetime import datetime
from typing import List
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
from ..schemas import users as users_schemas
import logging
from .. import user_permissions

router = APIRouter(prefix="/offer", tags=["Offer Body"])


@router.get(
    "/client/{offer_id}",
    response_model=List[products.ProductOut],
    status_code=status.HTTP_200_OK,
)
def get_offer_client(
    offer_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    query = (
        db.query(table_models_required.OffersBody)
        .join(
            table_models_required.CompanyConnections,
            table_models_required.CompanyConnections.offer_id
            == table_models_required.OffersBody.offer_id,
        )
        .where(table_models_required.OffersBody.offer_id == offer_id)
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.worker | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = query.filter(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
        case _:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authorised")
    try:
        prod = db.scalars(query).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer does not exists or it does not have any products",
        )
    return prod


@router.get(
    "/client/product/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=products.ProductOut,
)
def get_client_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    """
    This endpoint should be used only by sellers. If the owner of the product will access  this, it will cannot see it
    it should use instead get method with the route: /{product_id}"
    """
    query = (
        db.query(table_models_required.OffersBody)
        .join(
            table_models_required.CompanyConnections,
            table_models_required.CompanyConnections.offer_id
            == table_models_required.OffersBody.offer_id,
        )
        .where(table_models_required.OffersBody.id == product_id)
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.worker | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = query.filter(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised"
            )
    response = db.scalars(query).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found or you don't have the permission to view it",
        )
    return response


@router.get(
    "/all/{offer_id}",
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
    products_from_offers = db.scalars(query).all()
    print(products_from_offers)
    if not products_from_offers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer does not exists or it does not have any products",
        )
    # print(f"Query: {query}")
    # need redone, too long
    match user.role:
        case users_schemas.Roles.app_admin:
            try:
                response = db.scalars(query).all()
                return response

            except Exception as e:
                logging.error(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer body not found",
                )
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.worker:
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
                    detail="Offer body not found or you don't have permission to see it",
                )
        case users_schemas.Roles.custom:
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
                    detail="Offer body not found 2",
                )


@router.get(
    "/product/{product_id}",
    response_model=products.ProductOut2,
    status_code=status.HTTP_200_OK,
)
def get_product_from_offer(
    product_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    query = select(table_models_required.OffersBody).where(
        table_models_required.OffersBody.id == product_id
    )
    product: products.ProductOut2 = db.scalars(query).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager | users_schemas.Roles.user:
            if user.company_key != product.offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
        case users_schemas.Roles.custom:
            if user.company_key != product.offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            if user_permissions.can_view_offer(user.id, db) == False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )
    return product


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
    # need redone, too long
    match user.role:
        case users_schemas.Roles.app_admin:
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
        case users_schemas.Roles.admin | users_schemas.Roles.user:
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
        case users_schemas.Roles.custom:
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
    # need redone, too long
    match user.role:
        case users_schemas.Roles.app_admin:
            db.delete(table_models_required.OffersBody, id=product_id)
            db.commit()
            logging.info(
                f"{datetime.utcnow()} Product {product_id} was deleted from {offer.offer_name}"
            )
            return {
                "message": f"Product {product_id} was deleted from {offer.offer_name}"
            }
        case users_schemas.Roles.admin | "manager":
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
        case users_schemas.Roles.custom:
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
    # need redone, to long
    try:
        product: products.ProductOut = (
            db.query(table_models_required.OffersBody)
            .filter(table_models_required.OffersBody.id == product_id)
            .first()
        )
    except Exception as e:
        logging.error(f"{datetime.utcnow()} {product_id}: Product not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist",
        )
    # offer: offers.OffersRetrieve = db.get(table_models_required.Offers, product.offer_id)
    match user.role:
        case users_schemas.Roles.app_admin:
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
                db.refresh(product)
                logging.info(f"{datetime.utcnow()} {product_id}: Product Updated")
                return response

            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

        case users_schemas.Roles.admin | users_schemas.Roles.manager:
            offer: offers_schemas.Offers = db.get(Offers, product.offer_id)
            if user.company_key != offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not your product"
                )
            try:
                query = (
                    update(table_models_required.OffersBody)
                    .where(table_models_required.OffersBody.id == product_id)
                    .values(**product_update.model_dump())
                    .returning(OffersBody)
                )
                response = db.scalars(query).first()
                db.commit()
                db.refresh(product)
                logging.info(f"{datetime.utcnow()} {product_id}: Product Updated")
                return response

            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
        case users_schemas.Roles.custom:
            offer: offers_schemas.Offers = db.get(Offers, product.offer_id)
            if user.company_key != offer.company_key:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not your product"
                )
            if not user_permissions.can_create_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            try:
                query = (
                    update(table_models_required.OffersBody)
                    .where(table_models_required.OffersBody.id == product_id)
                    .values(**product_update.model_dump())
                    .returning(OffersBody)
                )
                response = db.scalars(query).first()
                db.commit()
                db.refresh(product)
                logging.info(f"{datetime.utcnow()} {product_id}: Product Updated")
                return response

            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )
