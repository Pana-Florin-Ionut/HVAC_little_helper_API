from fastapi import Depends
from pytest import Session
from sqlalchemy import select
from .. import table_models_required

from ..database import get_db


def check_company_exists(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Companies).where(
        table_models_required.Companies.id == company_id
    )
    # print(query, db.execute(query).first())
    return db.execute(query).first()

def check_company_has_projects(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.company_id == company_id
    )
    return db.execute(query).first()

def check_project_exists(project_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.id == project_id
    )
    return db.execute(query).first()

def get_company_projects(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.company_id == company_id
    )
    return db.execute(query).all()

def get_company_details(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Companies).where(
        table_models_required.Companies.id == company_id
    )
    return db.scalars(query).first()