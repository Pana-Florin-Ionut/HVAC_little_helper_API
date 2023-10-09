from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
import psycopg2
from sqlalchemy import delete, exists, insert, select
import sqlalchemy

from app.routers.utils import check_if_user_can_see_offer

from .. import user_permissions
from .. import oauth2, table_models_required
from ..schemas import users as users_schemas
from ..schemas import company_connections as company_connections_schemas
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import update


router = APIRouter(prefix="/company_connections", tags=["company_connections"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[company_connections_schemas.CompanyConnectionsFull],
)
def get_all_company_friends(
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    skip: Optional[int] = 0,
    limit: Optional[int] = 100,
    # search: Optional[str] = None, #cannot search for anything
):
    query = select(table_models_required.CompanyConnections)

    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_user(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised"
            )
    if skip:
        query = query.offset(skip)
    if limit:
        query = query.limit(limit)
    try:
        response = db.scalars(query).all()
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=company_connections_schemas.CompanyConnectionsFull,
)
def get_one_company_friend(
    id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    query = select(table_models_required.CompanyConnections)
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_user(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised"
            )
    query = query.where(table_models_required.CompanyConnections.id == id)

    try:
        response = db.scalars(query).first()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company Connection not found",
        )
    return response


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=company_connections_schemas.CompanyConnectionsFull,
)
def add_company_connection(
    new_connection: company_connections_schemas.CompanyConnectionsIn,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    if user.company.id == new_connection.friend_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company and Friend cannot be the same",
        )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            if not check_if_user_can_see_offer(
                new_connection.offer_id, user.company_key, db
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="There is no offer with that id or you cannot view it",
                )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_user(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="There is no offer with that id or you cannot view it",
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised"
            )

    try:
        new_connection = table_models_required.CompanyConnections(
            **new_connection.model_dump(), company_id=user.company.id
        )
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        return new_connection
    except sqlalchemy.exc.IntegrityError as e:
        # pgcode 23505 means psycopg2.errors.ForeignKeyViolation
        # print(e.orig.pgcode)
        if e.orig.pgcode == "23503":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend with the given id is not exists",
            )
        if e.orig.pgcode == "23505":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company Connection already exists",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_connection(
    id: int,
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    query = delete(table_models_required.CompanyConnections)
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised"
            )
    query = query.where(table_models_required.CompanyConnections.id == id)
    deleted = db.execute(query)
    if deleted.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company Connection not found"
        )
    db.commit()


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=company_connections_schemas.CompanyConnectionsFull,
)
def update_company_connection(
    id: int,
    body: company_connections_schemas.CompanyConnectionsIn,
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if body.friend_id == user.company.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company and Friend cannot be the same",
        )
    query = update(table_models_required.CompanyConnections)

    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            query = query.where(
                table_models_required.CompanyConnections.company_id == user.company.id
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised"
            )

    query = query.where(table_models_required.CompanyConnections.id == id)
    query = query.values(**body.model_dump())
    query = query.returning(table_models_required.CompanyConnections)
    # print(query)
    updated = db.scalars(query).first()
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company Connection not found"
        )
    db.commit()
    db.refresh(updated)
    return updated
