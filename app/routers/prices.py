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


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[prices_schemas.ProductWithPrices],
)
async def get_product_prices(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    query = select(
        table_models_required.OffersBody,
        table_models_required.OfferPrices,
    ).join(table_models_required.OfferPrices)
    response = db.execute(query).all()
    final_response = []
    for result in response:
        offer_body: products_schemas.ProductOut = result[0]
        offer_price: prices_schemas.PricesOut = result[1]  # Access the price directly
        product_with_prices = prices_schemas.ProductWithPrices(
            id=offer_body.id,
            offer_id=offer_body.offer_id,
            product_key=offer_body.product_key,
            product_name=offer_body.product_name,
            ch_1=offer_body.ch_1,
            ch_2=offer_body.ch_2,
            ch_3=offer_body.ch_3,
            ch_4=offer_body.ch_4,
            ch_5=offer_body.ch_5,
            ch_6=offer_body.ch_6,
            ch_7=offer_body.ch_7,
            ch_8=offer_body.ch_8,
            um=offer_body.um,
            quantity=offer_body.quantity,
            created_by=offer_body.created_by,
            created=offer_body.created,
            owner=offer_body.owner,
            offering_company=offer_price.offering_company,
            offer_product_id=offer_price.offer_product_id,
            price=offer_price.price,
        )
        final_response.append(product_with_prices)
    return final_response
