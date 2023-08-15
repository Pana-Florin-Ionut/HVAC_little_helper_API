from sqlalchemy import select
from . import table_models_required
from sqlalchemy.orm import Session


def can_view_offer(user_id: int, db: Session) -> bool:
    # Correct way to use it, it returns a bool
    query = select(table_models_required.Permissions.can_view_offer).where(
        table_models_required.Permissions.user_id == user_id
    )

    view_offer_permission = db.scalars(
        query
    ).first()  # we should search if db.scalar(query) is working
    return view_offer_permission


def can_create_project(user_id: int, db: Session) -> bool:
    query = select(table_models_required.Permissions.can_create_project).where(
        table_models_required.Permissions.user_id == user_id
    )
    can_create_project = db.scalars(query).first()
    return can_create_project


def can_edit_user(user_id: int, db: Session) -> bool:
    query = select(table_models_required.Permissions.can_edit_user).where(
        table_models_required.Permissions.user_id == user_id
    )
    can_edit_user = db.scalars(query).first()
    return can_edit_user


def can_view_user(user_id: int, db: Session) -> bool:
    query = select(table_models_required.Permissions.can_view_user).where(
        table_models_required.Permissions.user_id == user_id
    )
    can_view_user = db.scalars(query).first()
    return can_view_user


def can_create_offer(user_id: int, db: Session) -> bool:
    # create_offer_permission = (
    #     db.query(table_models_required.Permissions.can_create_offer)
    #     .filter(table_models_required.Permissions.user_id == user_id)
    #     .first()
    # )
    query = select(table_models_required.Permissions.can_create_offer).where(
        table_models_required.Permissions.user_id == user_id
    )
    create_offer_permission = db.scalars(query).first()
    return create_offer_permission


# Need redone
def can_view_project(user_id: int, db: Session) -> bool:
    query = select(table_models_required.Permissions.can_view_offer).where(
        table_models_required.Permissions.user_id == user_id
    )
    view_project_permission = db.scalar(query)
    print(view_project_permission)
    return view_project_permission


def can_create_product(user_id: int, db: Session) -> bool:
    create_product_permission = (
        db.query(table_models_required.Permissions.can_create_product)
        .filter(table_models_required.Permissions.user_id == user_id)
        .first()
    )
    return create_product_permission


def can_view_product(user_id: int, db: Session) -> bool:
    view_product_permission = (
        db.query(table_models_required.Permissions.can_view_product)
        .filter(table_models_required.Permissions.user_id == user_id)
        .first()
    )
    return view_product_permission
