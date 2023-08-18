from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from . import utils
from app.schemas import companies, offer_body, offers, products
from .utils import get_offer_details_id, get_product_from_offer
from sqlalchemy import Subquery, select, update, insert, delete, MappingResult
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

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[prices_schemas.PricesOut]
)
def get_prices(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    """
    Get all prices.
    """
    prices = db.query(table_models_required.OfferPrices).all()
    return prices
