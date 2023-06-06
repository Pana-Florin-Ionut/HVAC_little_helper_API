from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import schemas, table_models_required
from ..database import get_db
from .. import oauth2


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[schemas.CompanyOut]
)
def get_companies(
    db: Session = Depends(get_db),
    user=Depends(oauth2.get_current_user),
    limit: int = 100,
    skip: int = 0,
    company_name: str = "",
    company_key: str = "",
):
    match user.role:
        case "application_administrator":
            return db.scalars(
                select(table_models_required.Companies)
                .where(
                    table_models_required.Companies.company_name.icontains(company_name)
                )
                .where(
                    table_models_required.Companies.company_key.icontains(company_key)
                )
            ).all()
        case "test_user":
            return (
                db.query(table_models_required.Companies)
                .limit(limit)
                .offset(skip)
                .all()
            )
        case "admin", "manager":
            return (
                db.query(table_models_required.Companies)
                .where(table_models_required.Companies.is_verified == True)
                .limit(limit)
                .offset(skip)
                .all()
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.CompanyOut
)
def create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case "application_administrator":
            company = company.dict()
            company["is_verified"] = True
            db_company = table_models_required.Companies(**company)
            db.add(db_company)
            db.commit()
            db.refresh(db_company)
            return db_company
        case "test_user":
            db_company = table_models_required.Companies(**company)
            db.add(db_company)
            db.commit()
            db.refresh(db_company)
            return db_company
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )
