import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from . import utils
from app.schemas import companies, offer_body, offers, products
from sqlalchemy import Subquery, select, text, update, insert, delete, MappingResult
from .. import oauth2, table_models_required
from .. import user_permissions
from ..schemas import offers as offers_schemas
from ..schemas import prices as prices_schemas
from ..schemas import products as products_schemas
from ..schemas import users as users_schemas


router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=products_schemas.ProductOutFull,
)
def create_product(
    product: products_schemas.ProductIn,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    # need to add switch for user roles
    new_product = table_models_required.Products(
        **product.model_dump(),
        company_id=user.company.id,
        created_by=user.id,
        created=datetime.datetime.now()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product
