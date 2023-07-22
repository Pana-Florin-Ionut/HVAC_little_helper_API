import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from . import offer as create_offer_table
import sqlalchemy
from sqlalchemy import select, update, delete, insert
from .. import oauth2, table_models_required
from ..schemas import offers as offer_schemas
from ..schemas import users as users_schemas
from sqlalchemy.orm import Session
from ..database import get_db
from .. import user_permissions


router = APIRouter(prefix="/offers", tags=["Offers"])


# here should we have a group/filter/limit/sort/search/etc.
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[offer_schemas.OffersRetrieve],
)
async def offers(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    company_key: str = "",
    offer_key: str = "",
    search="",
    created_by: int = 0,
    limit: int = 100,
    skip: int = 0,
):
    print(f"User: {user.role}")
    match user.role:
        case "application_administrator":
            try:
                query = select(table_models_required.Offers)
                if company_key != "":
                    query = query.where(
                        table_models_required.Offers.company_id == company_key
                    )
                if offer_key != "":
                    query = query.where(
                        table_models_required.Offers.offer_key == offer_key
                    )
                if search != "":
                    query = query.where(
                        table_models_required.Offers.offer_name.contains(search)
                    )
                if created_by > 0:
                    query = query.where(
                        table_models_required.Offers.created_by == created_by
                    )
                query = query.limit(limit).offset(skip)
                return db.scalars(query).all()

            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bad request",
                )
        case "admin":
            try:
                query = select(table_models_required.Offers).where(
                    table_models_required.Offers.company_id == user.company_id
                )
                if company_key != "":
                    query = query.where(
                        table_models_required.Offers.company_id == company_key
                    )
                if offer_key != "":
                    query = query.where(
                        table_models_required.Offers.offer_key == offer_key
                    )
                if search != "":
                    query = query.where(
                        table_models_required.Offers.offer_name.contains(search)
                    )
                if created_by > 0:
                    query = query.where(
                        table_models_required.Offers.created_by == created_by
                    )
                query = query.limit(limit).offset(skip)
                return db.scalars(query).all()

            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bad request",
                )
        case "custom":
            permissions = user_permissions.can_view_offer(user.id, db)
            match permissions:
                case True:
                    try:
                        query = select(table_models_required.Offers).where(
                            table_models_required.Offers.company_id == user.company_id
                        )
                        if company_key != "":
                            query = query.where(
                                table_models_required.Offers.company_id == company_key
                            )
                        if offer_key != "":
                            query = query.where(
                                table_models_required.Offers.offer_key == offer_key
                            )
                        if search != "":
                            query = query.where(
                                table_models_required.Offers.offer_name.contains(search)
                            )
                        if created_by > 0:
                            query = query.where(
                                table_models_required.Offers.created_by == created_by
                            )
                        query = query.limit(limit).offset(skip)
                        response = db.scalars(query).all()
                        return response
                    except Exception as e:
                        print(e)
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Bad request",
                        )
                case _:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authorized to perform this action",
                    )


@router.post(
    "/admin",
    status_code=status.HTTP_201_CREATED,
    response_model=offer_schemas.OffersRetrieve,
)
def create_offer_admin(
    offer: offer_schemas.OffersCreateAdmin,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case "application_administrator":
            try:
                new_offer = table_models_required.Offers(
                    created_by=user.id, **offer.dict()
                )
                db.add(new_offer)
                db.commit()
                db.refresh(new_offer)

                return new_offer

            except sqlalchemy.exc.IntegrityError as e:
                if e.orig.pgcode == "23505":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="An offer with this name already exists of key exists",
                    )
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bad request",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to perform this admin action",
            )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=offer_schemas.OffersRetrieve,
)
def create_offer(
    offer: offer_schemas.OffersCreateUser,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case "admin" | "user":
            try:
                new_offer = table_models_required.Offers(
                    created_by=user.id, company_id=user.company_id, **offer.dict()
                )
                db.add(new_offer)
                db.commit()
                db.refresh(new_offer)

                return new_offer

            except sqlalchemy.exc.IntegrityError as e:
                if e.orig.pgcode == "23505":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="An offer with this name already exists",
                    )
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bad request",
                )
    # print(offer)
    if user_permissions.can_create_offer(user.id, db):
        try:
            new_offer = table_models_required.Offers(
                created_by=user.id, company_id=user.company_id, **offer.dict()
            )
            db.add(new_offer)
            db.commit()
            db.refresh(new_offer)

        except sqlalchemy.exc.IntegrityError as e:
            if e.orig.pgcode == "23505":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An offer with this name already exists",
                )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bad request",
            )

        return new_offer
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action",
        )
