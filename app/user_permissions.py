from . import schemas
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .utils import get_offer_details


def check_user_permissions(offer_name: str, user: schemas.UserOut, db: Session):
    if user.company_id == get_offer_details(
        offer_name, db
    ).company_id and user.role in ["admin", "manager"]:
        # user.role in db.query(table_models_required.Roles)
        # .where(table_models_required.Roles.company_id == user.company_id)
        # .first():
        return True
    elif user.role == "administrator":
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
