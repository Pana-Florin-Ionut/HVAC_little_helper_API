from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from . import utils
from app.schemas import companies, offer_body, offers, products
from .utils import get_offer_details_id, get_product_from_offer
from sqlalchemy import Subquery, select, text, update, insert, delete, MappingResult
from sqlalchemy.orm import with_parent
from ..table_models_required import Offers, OffersBody
from .. import oauth2, table_models_required, table_models_optional, tables
from ..schemas import offers as offers_schemas
from ..schemas import prices as prices_schemas
from ..schemas import products as products_schemas
from ..schemas import users as users_schemas
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import users as users_schemas
import logging
from sqlalchemy.orm import aliased
from sqlalchemy import exists
from .. import user_permissions


router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[prices_schemas.ProductWithPrices],
)
def get_offer_with_prices(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str = None,
    product_id: int = None,
):
    """
    This will return all the prices for the requesting company - buyer
    """
    query = (
        select(
            table_models_required.OfferPrices,
            table_models_required.OffersBody,
            table_models_required.Offers,
        )
        .select_from(table_models_required.OfferPrices)
        .join(
            OffersBody,
            OffersBody.id == table_models_required.OfferPrices.offer_product_id,
        )
        .join(Offers, Offers.id == OffersBody.offer_id)
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.OfferPrices.product.has(
                    table_models_required.Offers.company_key == user.company_key
                )
            )
        case _:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authorised")
    if search is not None:
        query = query.where(
            table_models_required.OffersBody.product_name.contains(search)
        )
    if product_id is not None:
        query = query.where(table_models_required.OffersBody.id == product_id)
    query = query.limit(limit).offset(skip)
    try:
        result = db.scalars(query).all()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Error, {e}",
        )


@router.get(
    "/clients",
    status_code=status.HTTP_200_OK,
    response_model=list[prices_schemas.ProductWithPrices],
)
def get_all_product_from_clients(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str = None,
):
    """
    This will return all the prices for offering company
    """
    query = (
        select(
            table_models_required.OfferPrices,
            table_models_required.OffersBody,
            table_models_required.Offers,
        )
        .select_from(table_models_required.OfferPrices)
        .join(
            OffersBody,
            OffersBody.id == table_models_required.OfferPrices.offer_product_id,
        )
        .join(Offers, Offers.id == OffersBody.offer_id)
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass

        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            # permision = check_company_friend()
            query = query.where(
                table_models_required.OfferPrices.offering_company == user.company.id
            )

        case users_schemas.Roles.custom:
            if not user_permissions.can_view_user(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.OfferPrices.offering_company == user.company.id
            )
        case _:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authorised")
    if search:
        query = query.where(
            table_models_required.OffersBody.product_name.icontains(search)
        )
    query = query.limit(limit).offset(skip)

    try:
        return db.scalars(query).all()
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[prices_schemas.ProductWithPrices],
)
# if the product has multiple prices, it will return all of them
def get_product_with_price(
    product_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    # query = query.limit(limit).offset(skip) should not have skip and offset. Maybe if there are too many prices for a single product we might implement this
    # skip: int = 0,
    # limit: int = 100,
):
    """
    This will allow the Client company that created the offer request to see the price for a particular item from all the
    """
    query = (
        select(
            table_models_required.OfferPrices,
            table_models_required.OffersBody,
            table_models_required.Offers,
        )
        .select_from(table_models_required.OfferPrices)
        .join(
            OffersBody,
            OffersBody.id == table_models_required.OfferPrices.offer_product_id,
        )
        .join(Offers, Offers.id == OffersBody.offer_id)
    ).where(table_models_required.OffersBody.id == product_id)
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.OfferPrices.product.has(
                    table_models_required.Offers.company_key == user.company_key
                )
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = query.where(
                table_models_required.OfferPrices.product.has(
                    table_models_required.Offers.company_key == user.company_key
                )
            )
        case _:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authorised")
    # query = query.limit(limit).offset(skip) should not have skip and offset. Maybe if there are too many prices for a single product we might implement this
    try:
        response = db.scalars(query).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Error, {e}",
        )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with the id {product_id} does not exist or you don't have permisions to view it",
        )
    return response


@router.post(
    "/{product_id}",
    # response_model=prices_schemas.ProductWithPrices,
    status_code=status.HTTP_201_CREATED,
)
def add_price(
    product_id: int,
    # price_for_product: prices_schemas.PricesOut,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    """
    Function need to check if the user that is making this post has access to the Product, or is from a friend company
    """
    query = (
        select(
            table_models_required.OfferPrices,
            table_models_required.OffersBody,
            table_models_required.Offers,
        )
        .select_from(table_models_required.OfferPrices)
        .join(
            OffersBody,
            OffersBody.id == table_models_required.OfferPrices.offer_product_id,
        )
        .join(Offers, Offers.id == OffersBody.offer_id)
    ).where(table_models_required.OffersBody.id == product_id)
    product = db.scalars(query).first()
    print(product)

    return product


@router.put(
    "/{product_id}",
    response_model=prices_schemas.ProductWithPrices,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_price(
    product_id: int,
    update_product: prices_schemas.PricesOut,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    """
    Function need to check if the user that is making this post has access to the Product, or is from a friend company
    """
    pass


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price(
    product_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    """
    Funtion need to check if the user was the creator of the price
    """
    pass


def check_company_friend(
    offer_id: int,
    offer_company_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    can_view = (
        db.query(exists().table_models_required.CompanyConnections)
        .where(table_models_required.CompanyConnections.friend_id == user.company.id)
        .where(table_models_required.CompanyConnections.company_id == offer_company_id)
        .where(table_models_required.CompanyConnections.offer_id == offer_id)
        .first()
    )
    print(can_view)
