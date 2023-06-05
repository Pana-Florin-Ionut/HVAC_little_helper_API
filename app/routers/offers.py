import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from . import offer as create_offer_table

import sqlalchemy
from .. import schemas, oauth2, table_models_required
from sqlalchemy.orm import Session
from ..database import get_db
from .. import user_permissions


router = APIRouter(prefix="/offers", tags=["Offers"])


# here should we have a group/filter/limit/sort/search/etc.
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.OffersRetrieve],
)
async def offers(
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    company_id=None,
    search=None,
    sort=None,
    filter=None,
    created_by=None,
):
    print(f"User: {user.role}")
    match user.role:
        case "application_administrator":
            try:
                offers = (
                    db.query(table_models_required.Offers)
                    .limit(limit)
                    .offset(skip)
                    .where(table_models_required.Offers.company_id == company_id)
                    .where(table_models_required.Offers.offer_name.contains(search))
                    .where(table_models_required.Offers.created_by == created_by)
                    .filter(filter)
                    .sort(sort)
                    .all()
                )
                return offers
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bad request",
                )
        case "admin":
            offers = (
                db.query(table_models_required.Offers)
                .limit(limit)
                .offset(skip)
                .where(table_models_required.Offers.company_id == user.company_id)
                .where(table_models_required.Offers.offer_name.contains(search))
                .where(table_models_required.Offers.created_by == created_by)
                .filter(filter)
                .sort(sort)
                .all()
            )
            return offers
        case "custom":
            if user_permissions.can_view_offer(user.id, db):
                try:
                    offers = (
                db.query(table_models_required.Offers)
                .limit(limit)
                .offset(skip)
                .where(table_models_required.Offers.company_id == user.company_id)
                .where(table_models_required.Offers.offer_name.contains(search))
                .where(table_models_required.Offers.created_by == created_by)
                .filter(filter)
                .sort(sort)
                .all()
            )
                    return offers
                except Exception as e:
                    print(e)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Bad request",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authorized to perform this action",
                )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.OffersRetrieve,
)
def create_offer(
    offer: schemas.OffersCreate,
    db: Session = Depends(get_db),
    user: int = Depends(oauth2.get_current_user),
):
    # print(offer)
    if user_permissions.can_create_offer(user.id, db):
        try:
            new_offer = table_models_required.Offers(created_by=user.id, **offer.dict())
            db.add(new_offer)
            db.commit()
            db.refresh(new_offer)
            # Create offer table after is ok
            create_offer_table.create_offer_table(
                offer_name=offer.offer_name, user=user, db=db
            )

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
