from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from .. import schemas, table_models_required
from ..database import get_db
from .. import oauth2
from sqlalchemy import update


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[schemas.CompanyOut]
)
def get_companies(
    db: Session = Depends(get_db),
    user=Depends(oauth2.get_current_user),
    company_name: str = "",
    company_key: str = "",
    limit: int = 100,
    skip: int = 0,
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
                .limit(limit)
                .offset(skip)
            ).all()
        case "test_user":
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
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.CompanyOut
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


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    query = delete(table_models_required.Companies).where(table_models_required.Companies.id == company_id).returning(table_models_required.Companies.id)
    print(query)
    id = db.execute(query).fetchone()
    if id == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} does not exist",
        )
    db.commit()

@router.put("/{company_id}", status_code=status.HTTP_202_ACCEPTED)
def update_company(company_id: int, company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    query = update(table_models_required.Companies).where(table_models_required.Companies.id == company_id).values(**company.dict()).returning(table_models_required.Companies.id)
    id = db.execute(query).fetchone()
    if id == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} does not exist",
        )
    db.commit()
