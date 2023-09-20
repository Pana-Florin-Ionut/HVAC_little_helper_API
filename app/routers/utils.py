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


def check_offer_product_exist_admin(
    product_id: int, db: Session = Depends(get_db)
) -> bool:
    offer_product_exist = db.query(
        exists().where(table_models_required.OffersBody.id == product_id)
    ).scalar()
    return offer_product_exist


def check_company_exists(company_id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.Companies).where(
        table_models_required.Companies.id == company_id
    )
    # print(query, db.execute(query).first())
    return db.execute(query).first()


def check_product_exist_for_user(
    product_id: int, user_company_key: str, db: Session = Depends(get_db)
):
    product_exist = (
        db.query(table_models_required.OffersBody)
        .where(table_models_required.OffersBody.id == product_id)
        .where(table_models_required.Offers.company_key == user_company_key)
    ).join(
        table_models_required.Offers,
        table_models_required.Offers.id == table_models_required.OffersBody.offer_id,
    )

    return product_exist.scalar()


def check_product_exist_for_user_admin(
    product_id: int, company_id: int, db: Session = Depends(get_db)
):
    """
    Check if price exist for offering company and product

    """
    product_is_existing = db.query(
        exists()
        .where(table_models_required.OfferPrices.offer_product_id == product_id)
        .where(table_models_required.OfferPrices.offering_company == company_id)
    )
    return product_is_existing.scalar()


def check_product_with_price_exist(product_id: int, db: Session = Depends(get_db)):
    query = (
        select(
            table_models_required.OfferPrices,
            table_models_required.OffersBody,
            table_models_required.Offers,
        )
        .select_from(table_models_required.OfferPrices)
        .join(
            table_models_required.OffersBody,
            table_models_required.OffersBody.id
            == table_models_required.OfferPrices.offer_product_id,
        )
        .join(
            table_models_required.Offers,
            table_models_required.Offers.id
            == table_models_required.OffersBody.offer_id,
        )
    ).where(table_models_required.OffersBody.id == product_id)

    product_with_price = db.scalars(query).first()
    if product_with_price:
        return True
    return False


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


def get_product_from_offer(id: int, db: Session = Depends(get_db)):
    query = select(table_models_required.OffersBody).where(
        table_models_required.OffersBody.offer_id == id
    )
    return db.scalars(query).first()
