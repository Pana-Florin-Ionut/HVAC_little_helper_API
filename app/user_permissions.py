from . import table_models_required
from sqlalchemy.orm import Session



def can_create_project(user_id: int, db: Session):
    create_project_permission = (
        db.query(table_models_required.Roles.can_create_project)
        .filter(table_models_required.Roles.user_id == user_id)
        .first()
    )
    return create_project_permission


def can_view_project(user_id: int, db: Session):
    view_project_permission = (
        db.query(table_models_required.Roles.can_view_project)
        .filter(table_models_required.Roles.user_id == user_id)
        .first()
    )
    return view_project_permission


def can_create_offer(user_id: int, db: Session):
    create_offer_permission = (
        db.query(table_models_required.Roles.can_create_offer)
        .filter(table_models_required.Roles.user_id == user_id)
        .first()
    )
    return create_offer_permission


def can_view_offer(user_id: int, db: Session):
    view_offer_permission = (
        db.query(table_models_required.Roles.can_view_offer)
        .filter(table_models_required.Roles.user_id == user_id)
        .first()
    )
    return view_offer_permission

def can_create_product(user_id: int, db: Session):
    create_product_permission = (
        db.query(table_models_required.Roles.can_create_product)
        .filter(table_models_required.Roles.user_id == user_id)
        .first()
    )
    return create_product_permission


def can_view_product(user_id: int, db: Session):
    view_product_permission = (
        db.query(table_models_required.Roles.can_view_product)
        .filter(table_models_required.Roles.user_id == user_id)
        .first()
    )
    return view_product_permission

