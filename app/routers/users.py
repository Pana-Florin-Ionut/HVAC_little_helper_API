from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from app.user_permissions import can_edit_user, can_view_user

from .. import oauth2
from .. import utils, table_models_required
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import users as users_schemas
from sqlalchemy import select
import sqlalchemy.exc as exc
import logging
from ..roles import Roles

router = APIRouter(prefix="/users", tags=["Users"])


# old method, uses json body for getting the results
# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=users_schemas.UserOut)
# def create_user(user: users_schemas.UserCreate, db: Session = Depends(get_db)):
#     try:
#         hashed_password = utils.hash(user.password)
#         user.password = hashed_password
#         new_user = table_models_required.Users(**user.dict())
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         return new_user
#     except exc.IntegrityError as e:
#         if e.orig.pgcode == "23505":
#             # 23505 code is psycopg error code for unique violation
#             logging.warn(f"{datetime.utcnow()} - User already exists: {e} ")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail=f"User already exists"
#             )
#         else:
#             logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating user"
#             )
#     except Exception as e:
#         logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating user"
#         )


# new methon, uses form body for getting the results
@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=users_schemas.UserOut
)
def create_user(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # This should send a email for confirmation

    try:
        hashed_password = utils.hash(user_credentials.password)
        user_credentials.password = hashed_password
        new_user = table_models_required.Users(
            email=user_credentials.username, password=user_credentials.password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except exc.IntegrityError as e:
        if e.orig.pgcode == "23505":
            # 23505 code is psycopg error code for unique violation
            logging.warn(f"{datetime.utcnow()} - User already exists: {e} ")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already exists",
            )
        else:
            logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating user",
            )
    except Exception as e:
        logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user",
        )


@router.put(
    "/admin/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=users_schemas.UserOut,
)
def update_user_by_administrator(
    id: int,
    update_user: users_schemas.UserUpdateAdministrator,
    actor_user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    user: users_schemas.UserUpdateAdministrator = db.get(
        table_models_required.Users, id
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found"
        )
    match actor_user.role:
        case Roles.app_admin:
            try:
                user.company_key = update_user.company_key
                user.role = update_user.role

                db.commit()
                db.refresh(user)
                return user
            except Exception as e:
                logging.warn(f"{datetime.utcnow()} - Error updating user: {e} ")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error updating user",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )


@router.put(
    "/{id}", status_code=status.HTTP_201_CREATED, response_model=users_schemas.UserOut
)
def update_user_by_admin(
    id: int,
    update_user: users_schemas.UserUpdate,
    actor_user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    user: users_schemas.UserOut = db.get(table_models_required.Users, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found"
        )
    match actor_user.role:
        case Roles.app_admin:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER, detail="URL/admin/{id}"
            )
        case Roles.admin:
            try:
                # Admins should be able to add just to their company
                user.company_key = actor_user.company_key
                user.role = update_user.role
                db.commit()
                db.refresh(user)
                return user
            except Exception as e:
                logging.warn(f"{datetime.utcnow()} - Error updating user: {e} ")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error updating user",
                )
        case Roles.custom:
            if can_edit_user(actor_user.id, db):
                try:
                    # Admins like users should be able to add just to their company
                    user.company_key = actor_user.company_key
                    user.role = update_user.role
                    db.commit()
                    db.refresh(user)
                    return user
                except Exception as e:
                    logging.warn(f"{datetime.utcnow()} - Error updating user: {e} ")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Error updating user",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[users_schemas.UserOut]
)
def get_all_users(
    actor: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    match actor.role:
        case Roles.app_admin:
            return db.query(table_models_required.Users).all()
        case Roles.admin:
            return (
                db.query(table_models_required.Users)
                .where(table_models_required.Users.company_key == actor.company_key)
                .where(table_models_required.Users.role == "")
                .all()
            )
        case Roles.custom:
            if not can_view_user(actor.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            return (
                db.query(table_models_required.Users)
                .where(table_models_required.Users.company_key == actor.company_key)
                .where(table_models_required.Users.role == "")
                .all()
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )


@router.get(
    "/admin", status_code=status.HTTP_200_OK, response_model=list[users_schemas.UserOut]
)
def get_all_users_by_admin(
    actor: users_schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    company_key: str = "",
    role: str = "",
    email: str = "",
    limit: int = 100,
    offset: int = 0,
):
    query = select(table_models_required.Users)
    if company_key:
        query = query.where(table_models_required.Users.company_key == company_key)
    if role:
        query = query.where(table_models_required.Users.role == role)
    if email:
        query = query.where(table_models_required.Users.email.ilike(email))
    query = query.limit(limit).offset(offset)
    match actor.role:
        case Roles.app_admin:
            return db.scalars(query).all()
        case Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=users_schemas.UserOut
)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    actor: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    user = db.get(table_models_required.Users, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found"
        )
    match actor.role:
        case Roles.app_admin:
            return user
        case Roles.admin:
            if user.company_key == None or user.company_key == actor.company_key:
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User not in your company",
                )
        case Roles.custom:
            if not can_view_user(actor.id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            if user.company_key == None or user.company_key == actor.company_key:
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User not in your company",
                )
