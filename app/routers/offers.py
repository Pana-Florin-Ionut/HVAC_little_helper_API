import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.routers.utils import (
    get_company_projects,
    get_project_key,
    match_project_company,
    match_user_company,
)
from . import offer_body as create_offer_table
import sqlalchemy
from sqlalchemy import select, update, delete, insert
from .. import oauth2, table_models_required
from ..schemas import offers as offer_schemas
from ..schemas import users as users_schemas
from sqlalchemy.orm import Session
from ..database import get_db
from .. import user_permissions
from ..schemas import users as users_schemas
from unittest import result


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
    project_key: str = "",
    offer_key: str = "",
    search="",
    created_by: int = 0,
    limit: int = 100,
    skip: int = 0,
):
    query = select(table_models_required.Offers)
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin:
            query = query.where(
                table_models_required.Offers.company_key == user.company_key
            )
        case users_schemas.Roles.custom:
            can_view_offers = user_permissions.can_view_offer(user.id, db)
            if not can_view_offers:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = query.where(
                table_models_required.Offers.company_key == user.company_key
            )

    if company_key != "":
        query = query.where(table_models_required.Offers.company_key == company_key)
    if project_key != "":
        query = query.where(table_models_required.Offers.project_key == project_key)
    if offer_key != "":
        query = query.where(table_models_required.Offers.offer_key == offer_key)
    if search != "":
        query = query.where(table_models_required.Offers.offer_name.contains(search))
    if created_by > 0:
        query = query.where(table_models_required.Offers.created_by == created_by)
    query = query.limit(limit).offset(skip)
    # print(f"Query: {query}")
    try:
        result = db.scalars(query).all()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
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
    try:
        offer.project_key = get_project_key(offer.project_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with the key {offer.project_key} does not exist",
        )
    if not match_project_company(offer.project_id, offer.company_key, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project and company do not match",
        )
    match user.role:
        case users_schemas.Roles.app_admin:
            try:
                new_offer = table_models_required.Offers(
                    created_by=user.id, **offer.model_dump()
                )
                db.add(new_offer)
                db.commit()
                db.refresh(new_offer)

                return new_offer

            except sqlalchemy.exc.IntegrityError as e:
                print(e)
                if e.orig.pgcode == "23505":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="An offer with this name already exists of key exists",
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Bad request",
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
    try:
        project_key = get_project_key(offer.project_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with the key {offer.project_key} does not exist",
        )

    match user.role:
        case users_schemas.Roles.admin | users_schemas.Roles.user:
            pass
        case users_schemas.Roles.custom:
            # print(offer)
            if not user_permissions.can_create_offer(user.id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to perform this action",
            )
    try:
        new_offer = table_models_required.Offers(
            created_by=user.id,
            company_key=user.company_key,
            project_key=project_key,
            **offer.model_dump(),
        )
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if e.orig.pgcode == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An offer with this name already exists",
            )
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request",
        )

    return new_offer


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer_id(
    offer_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case users_schemas.Roles.app_admin:
            try:
                query = select(table_models_required.Offers).where(
                    table_models_required.Offers.id == offer_id
                )
                db.delete(db.scalars(query).first())
                db.commit()

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


@router.put("/{offer_id}", response_model=offer_schemas.OffersRetrieve)
def update_offer(
    offer_id: int,
    offer: offer_schemas.OffersUpdate,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    current_offer: offer_schemas.OffersRetrieve = db.get(
        table_models_required.Offers, offer_id
    )
    if not current_offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer with id {offer_id} does not exist",
        )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.manager | users_schemas.Roles.user:
            if not match_user_company(user.company_key, offer_id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This offer is not from your company",
                )
        case users_schemas.Roles.custom:
            if not user_permissions.can_view_offer(
                user.id, db
            ) or not match_user_company(user.company_key, offer_id, db):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authorized to perform this action",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to perform this action",
            )
    try:
        # updating the values of the current_offer with the values received
        {setattr(current_offer, k, v) for k, v in offer.model_dump().items()}
        db.commit()
        db.refresh(current_offer)
        return current_offer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request",
        )


# here should we have a group/filter/limit/sort/search/etc.
@router.get(
    "/clients",
    status_code=status.HTTP_200_OK,
    response_model=List[offer_schemas.OffersSellersOut],
)
async def offers(
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
    company_key: str = "",
    project_key: str = "",
    offer_key: str = "",
    search="",
    limit: int = 100,
    skip: int = 0,
):
    query = db.query(table_models_required.Offers).join(
        table_models_required.CompanyConnections,
        table_models_required.CompanyConnections.offer_id
        == table_models_required.Offers.id,
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.manager | users_schemas.Roles.user:
            query = query.filter(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
        case users_schemas.Roles.custom:
            can_view_offers = user_permissions.can_view_offer(user.id, db)
            if not can_view_offers:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = query.filter(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )

    if company_key != "":
        query = query.where(table_models_required.Offers.company_key == company_key)
    if project_key != "":
        query = query.where(table_models_required.Offers.project_key == project_key)
    if offer_key != "":
        query = query.where(table_models_required.Offers.offer_key == offer_key)
    if search != "":
        query = query.where(table_models_required.Offers.offer_name.contains(search))
    query = query.limit(limit).offset(skip)
    # print(f"Query: {query}")
    try:
        result = db.scalars(query).all()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


# here should we have a group/filter/limit/sort/search/etc.
@router.get(
    "/clients/{offer_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[offer_schemas.OffersSellersOut],
)
async def offers(
    offer_id: int,
    db: Session = Depends(get_db),
    user: users_schemas.UserOut = Depends(oauth2.get_current_user),
):
    query = (
        db.query(table_models_required.Offers)
        .join(
            table_models_required.CompanyConnections,
            table_models_required.CompanyConnections.offer_id
            == table_models_required.Offers.id,
        )
        .where(table_models_required.Offers.id == offer_id)
    )
    match user.role:
        case users_schemas.Roles.app_admin:
            pass
        case users_schemas.Roles.admin | users_schemas.Roles.manager | users_schemas.Roles.user:
            query = query.filter(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
        case users_schemas.Roles.custom:
            can_view_offers = user_permissions.can_view_offer(user.id, db)
            if not can_view_offers:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
                )
            query = query.filter(
                table_models_required.CompanyConnections.friend_id == user.company.id,
            )
    try:
        result = db.scalars(query).all()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
