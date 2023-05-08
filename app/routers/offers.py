from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/offers", tags=["Offers"])
