from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.routers.naming_utils import update_projects
from .. import schemas, table_models_required
from ..database import get_db
from .. import oauth2
from sqlalchemy import update
from ..schemas import companies as companies_schema
from ..schemas import users as users_schemas
from .utils import check_company_exists, check_company_has_projects, get_company_details
import sqlalchemy
from ..schemas import users as users_schemas


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[companies_schema.CompanyOut]
)
def get_companies(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    company_name: str = "",
    company_key: str = "",
    limit: int = 100,
    skip: int = 0,
):
    match user.role:
        case users_schemas.Roles.app_admin:
            query = select(table_models_required.Companies)
            response = db.scalars(query).all()
            return response
        case users_schemas.Roles.test:
            return db.scalars(
                select(table_models_required.Companies)
                .where(
                    table_models_required.Companies.company_name.icontains(company_name)
                )
                .where(
                    table_models_required.Companies.company_key.icontains(company_key)
                )
                .limit(limit)
                .offset(skip)
            ).all()
        case users_schemas.Roles.admin:
            return (
                db.query(table_models_required.Companies)
                .where(table_models_required.Companies.is_verified == True)
                .where(
                    table_models_required.Companies.company_name.icontains(company_name)
                )
                .where(
                    table_models_required.Companies.company_key.icontains(company_key)
                )
                .where(table_models_required.Companies.id != user.company.id)
                .limit(limit)
                .offset(skip)
                .all()
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )


@router.get("/{company_id}", response_model=companies_schema.CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case users_schemas.Roles.app_admin:
            return get_company_details(company_id, db)
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=companies_schema.CompanyOut
)
def create_company(
    company: companies_schema.CompanyCreate,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case users_schemas.Roles.app_admin:
            try:
                company = company.model_dump()
                company["is_verified"] = True
                db_company = table_models_required.Companies(**company)
                db.add(db_company)
                db.commit()
                db.refresh(db_company)
                # print(db_company.company_key)
                return db_company
            except sqlalchemy.exc.IntegrityError as e:
                if e.orig.pgcode == "23505":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Company already exists",
                    )
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bad Request",
                )
        case users_schemas.Roles.test:
            try:
                company = company.model_dump()
                company["is_verified"] = True
                db_company = table_models_required.Companies(**company)
                db.add(db_company)
                db.commit()
                db.refresh(db_company)
                # print(db_company.company_key)
                return db_company
            except sqlalchemy.exc.IntegrityError as e:
                if e.orig.pgcode == "23505":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Company already exists",
                    )
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bad Request",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case users_schemas.Roles.app_admin:
            if not check_company_exists(company_id, db):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with id {company_id} does not exist",
                )
            query = (
                delete(table_models_required.Companies)
                .where(table_models_required.Companies.id == company_id)
                .returning(table_models_required.Companies.id)
            )
            db.execute(query)
            db.commit()
        case users_schemas.Roles.test:
            if not check_company_exists(company_id, db):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with id {company_id} does not exist",
                )
            query = (
                delete(table_models_required.Companies)
                .where(table_models_required.Companies.id == company_id)
                .returning(table_models_required.Companies.id)
            )
            db.execute(query)
            db.commit()
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )


@router.put("/{company_id}", status_code=status.HTTP_200_OK)
def update_company(
    company_id: int,
    updaded_company: companies_schema.CompanyUpdate,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    # Only company name can be updated
    match user.role:
        case users_schemas.Roles.app_admin:
            company: companies_schema.CompanyOut = get_company_details(company_id, db)
            company.company_name = updaded_company.company_name
            db.commit()
            db.refresh(company)
            return company
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )
