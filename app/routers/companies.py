from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/")
def get_companies():
    return {"message": "Companies"}
