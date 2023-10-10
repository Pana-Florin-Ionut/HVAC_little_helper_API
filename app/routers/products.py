import datetime
from fastapi import APIRouter, Depends, HTTPException, status
import psycopg2
import sqlalchemy
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
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            pass
        case users_schemas.Roles.custom:
            if not user_permissions.can_create_product(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
    try:
        new_product = table_models_required.Products(
            **product.model_dump(),
            company_id=user.company.id,
            created_by=user.id,
            created=datetime.datetime.now(),
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with these characteristics already exists",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return new_product


@router.get("", response_model=list[products_schemas.ProductOutFull])
def get_products(
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
    company_id: int = None,
    search: str = None,
):
    query = select(table_models_required.Products)
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_product(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
    if company_id:
        query = query.where(table_models_required.Products.company_id == company_id)
    if search:
        query = query.where(table_models_required.Products.product_name.ilike(search))
    if limit:
        query = query.limit(limit)
    if skip:
        query = query.offset(skip)

    try:
        return db.scalars(query).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{product_id}", response_model=products_schemas.ProductOutFull)
def get_one_product(
    product_id: int,
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    query = select(table_models_required.Products).where(
        table_models_required.Products.id == product_id
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_product(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
    try:
        response = db.scalar(query)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return response


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    query = delete(table_models_required.Products).where(
        table_models_required.Products.id == product_id
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_create_product(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
    try:
        response = db.execute(query)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if response.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    db.commit()


@router.put("/{product_id}", response_model=products_schemas.ProductOutFull)
def update_product(
    product: products_schemas.ProductIn,
    product_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    query = update(table_models_required.Products)
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_create_product(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.Products.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
    try:
        query = query.where(table_models_required.Products.id == product_id)
        query = query.values(**product.model_dump()).returning(
            table_models_required.Products
        )
        print(query)
        product_to_update = db.scalar(query)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not product_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    db.commit()
    db.refresh(product_to_update)
    return product_to_update
