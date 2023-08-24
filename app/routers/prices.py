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
from .. import user_permissions
from os.path import join

router = APIRouter(prefix="/prices", tags=["Prices"])


# @router.get(
#     "", status_code=status.HTTP_200_OK, response_model=list[prices_schemas.PricesOut]
# )
# def get_prices(
#     db: Session = Depends(get_db),
#     user: users_schemas.UserOut = Depends(oauth2.get_current_user),
# ):
#     """
#     Get all prices.
#     """
#     prices = db.query(table_models_required.OfferPrices).all()
#     return prices


def create_product_with_prices(
    product: products_schemas.ProductOut, price: prices_schemas.PricesOut
) -> prices_schemas.ProductWithPrices:
    product_with_prices = prices_schemas.ProductWithPrices(
        id=product.id,
        offer_id=product.offer_id,
        product_key=product.product_key,
        product_name=product.product_name,
        ch_1=product.ch_1,
        ch_2=product.ch_2,
        ch_3=product.ch_3,
        ch_4=product.ch_4,
        ch_5=product.ch_5,
        ch_6=product.ch_6,
        ch_7=product.ch_7,
        ch_8=product.ch_8,
        um=product.um,
        quantity=product.quantity,
        created_by=product.created_by,
        created=product.created,
        owner=product.owner,
        offering_company=price.offering_company,
        offer_product_id=price.offer_product_id,
        price=price.price,
    )
    return product_with_prices


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[prices_schemas.ProductWithPrices],
)
async def get_product_prices(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case users_schemas.Roles.app_admin:
            query = select(
                table_models_required.OffersBody,
                table_models_required.OfferPrices,
            ).join(table_models_required.OfferPrices)
            response = db.execute(query).all()
            final_response = []
            for resp in response:
                product = resp[0]
                price = resp[1]
                product_with_prices = create_product_with_prices(product, price)
                final_response.append(product_with_prices)
            return final_response
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = (
                select(
                    table_models_required.OffersBody,
                    table_models_required.OfferPrices,
                )
                .join(table_models_required.OfferPrices)
                .where(
                    table_models_required.OffersBody.offer.has(
                        table_models_required.Offers.company_key == user.company_key
                    )
                )
            )
            response = db.execute(query).all()
            final_response = []
            for resp in response:
                product = resp[0]
                price = resp[1]
                product_with_prices = create_product_with_prices(product, price)
                final_response.append(product_with_prices)
            return final_response
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = (
                select(
                    table_models_required.OffersBody,
                    table_models_required.OfferPrices,
                )
                .join(table_models_required.OfferPrices)
                .where(
                    table_models_required.OffersBody.offer.has(
                        table_models_required.Offers.company_key == user.company_key
                    )
                )
            )
            response = db.execute(query).all()
            final_response = []
            for resp in response:
                product = resp[0]
                price = resp[1]
                product_with_prices = create_product_with_prices(product, price)
                final_response.append(product_with_prices)
            return final_response
