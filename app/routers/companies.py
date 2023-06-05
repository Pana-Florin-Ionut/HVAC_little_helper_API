from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, table_models_required
from ..database import get_db


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/")
def get_companies(db: Session = Depends(get_db)):
    print(db.query(table_models_required.Companies).all())
    return db.query(table_models_required.Companies).all()

