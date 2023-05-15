from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, oauth2, table_models_required
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix="/offers", tags=["Offers"])


# here should we have a group/filter/limit/sort/search/etc.
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.OffersRetrieve],
)
async def offers(
    db: Session = Depends(get_db), user: int = Depends(oauth2.get_current_user)
):
    print(f"User: {user}")
    if user.company_id is None and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action",
        )
    if user.role == "admin":
        offers = db.query(table_models_required.Offers).all()
        return offers

    offers = (
        db.query(table_models_required.Offers)
        .where(table_models_required.Offers.company_id == user.company_id)
        .all()
    )
    return offers


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.OffersRetrieve,
)
async def create_offer(
    offer: schemas.OffersCreate,
    db: Session = Depends(get_db),
    user: int = Depends(oauth2.get_current_user),
):
    print(offer)
    if user.company_id is None and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action",
        )
    if (
        db.query(table_models_required.Offers)
        .filter(table_models_required.Offers.offer_name == offer.offer_name)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An offer with this name already exists",
        )

    new_offer = table_models_required.Offers(created_by=user.id, **offer.dict())
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer
    # except Exception as e:
    #     print(f"Error:  {e}")
    #     if (
    #         f'duplicate key value violates unique constraint "offers_offer_name_key"\nDETAIL:  Key (offer_name)=({offer_name}) already exists.\n'
    #         in str(e)
    #     ):
    #         conn.rollback()
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail=f"Offer already exists"
    #         )
    #         # return {"message": "Offer already exists"}

    #     conn.rollback()
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad request"
    #     )

    # print(offers_dict)
