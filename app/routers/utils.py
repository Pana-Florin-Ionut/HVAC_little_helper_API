from fastapi import Depends
from pytest import Session
from sqlalchemy import exists, select
from .. import table_models_required

from ..database import get_db


def check_user_exists(user_id: int, db: Session = Depends(get_db)) -> bool:
    user_exists = db.query(
        exists().where(table_models_required.Users.id == user_id)
    ).scalar()
    return user_exists


def check_company_exists(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Companies).where(
        table_models_required.Companies.id == company_id
    )
    # print(query, db.execute(query).first())
    return db.execute(query).first()


def project_exists_key(
    project_key: str, company_key: str, db: Session = Depends(get_db)
) -> bool:
    """
    Checks if a project exists with the given key for a company.
    :param project_key:
    :param company_key:
    :param db:
    :return bool:

    """
    is_present = db.query(
        exists()
        .where(table_models_required.Projects.project_key == project_key)
        .where(table_models_required.Projects.company.has(company_key=company_key))
    ).scalar()

    # print(query)
    return is_present


def project_exists_name(project_name: str, db: Session = Depends(get_db)) -> bool:
    is_present = db.query(
        exists().where(table_models_required.Projects.project_name == project_name)
    ).scalar()
    return is_present


def check_company_has_projects(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.company_id == company_id
    )
    return db.execute(query).first()


def check_project_exists_name(project_name: str, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.project_name == project_name
    )
    return db.execute(query).first()


def check_project_exists_key(project_key: str, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.project_key == project_key
    )
    return db.scalars(query).first()


def get_project_details_Co_key(
    project_key: str, company_key: str, db: Session = Depends(get_db)
):
    query = (
        select(table_models_required.Projects)
        .where(table_models_required.Projects.project_key == project_key)
        .where(table_models_required.Projects.company.has(company_key=company_key))
    )
    return db.scalars(query).first()


def get_project_details_Co_key(
    project_key: str, company_key: str, db: Session = Depends(get_db)
):
    query = (
        select(table_models_required.Projects)
        .where(table_models_required.Projects.project_key == project_key)
        .where(table_models_required.Projects.company_key == company_key)
    )
    return db.scalars(query).first()


def get_company_projects(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects).where(
        table_models_required.Projects.company_id == company_id
    )
    results = db.execute(query).all()
    print(results)
    return results


def get_company_details(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Companies).where(
        table_models_required.Companies.id == company_id
    )
    return db.scalars(query).first()


def get_project_key(project_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Projects.project_key).where(
        table_models_required.Projects.id == project_id
    )
    return db.scalar(query)


def match_project_company(
    project_id: int, company_key: str, db: Session = Depends(get_db)
) -> bool:
    is_match = db.query(
        exists()
        .where(table_models_required.Projects.company_key == company_key)
        .where(table_models_required.Projects.id == project_id)
    ).scalar()
    # print(is_present)

    return is_match


def match_user_company(
    user_company_key: str, offer_id: int, db: Session = Depends(get_db)
) -> bool:
    is_match = db.query(
        exists()
        .where(table_models_required.Offers.id == offer_id)
        .where(table_models_required.Offers.company_key == user_company_key)
    ).scalar()
    return is_match


def get_offer_details_id(id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Offers).where(
        table_models_required.Offers.id == id
    )
    return db.scalars(query).first()
