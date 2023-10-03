from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from .. import user_permissions
from .. import oauth2, table_models_required
from ..schemas import users as users_schemas
from ..schemas import company_connections as company_connections_schemas
from sqlalchemy.orm import Session
from ..database import get_db


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
