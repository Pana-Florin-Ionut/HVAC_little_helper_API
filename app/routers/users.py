from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, table_models_required
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import users as users_schemas
import sqlalchemy
import logging

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
#     except sqlalchemy.exc.IntegrityError as e:
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
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=users_schemas.UserOut)
def create_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # print(user_credentials)
    try:
        hashed_password = utils.hash(user_credentials.password)
        user_credentials.password = hashed_password
        new_user = table_models_required.Users(email=user_credentials.username, password=user_credentials.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except sqlalchemy.exc.IntegrityError as e:
        if e.orig.pgcode == "23505":
            # 23505 code is psycopg error code for unique violation
            logging.warn(f"{datetime.utcnow()} - User already exists: {e} ")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"User already exists"
            )
        else:
            logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating user"
            )
    except Exception as e:
        logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating user"
        )


@router.get("/{id}", response_model=users_schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = (
        db.query(table_models_required.Users)
        .filter(table_models_required.Users.id == id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )
    return user
