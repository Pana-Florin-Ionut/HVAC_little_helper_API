from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from . import table_models_optional
from .database import engine, get_db
from . import tables
from .database_model import Database as db
from . import schemas, oauth2
from .database_connection import conn
from . import user_permissions

from .routers import companies, offer, projects, users, offers, auth
from . import table_models_required


# class Offer(BaseModel):

db = db(conn)

table_models_required.Base.metadata.create_all(bind=engine)


offers_table = "offers"


app = FastAPI()

app.include_router(projects.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(offer.router)
app.include_router(offers.router)
app.include_router(auth.router)


@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}




@app.get("/offers/{id}")
async def get_offer(id: int):
    # print(offer)
    offer = "offer"
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} not found",
        )
    return offer


@app.put("/offers/{id}")
async def update_offer(id: int, offer: schemas.Offer):
    index = "offer"
    print("Index" + str(index))
    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} not found",
        )
    # offers_dict[id] = offer.dict()
    # return {"Offer updated": f"{id}: {find_offer(id)} "}


@app.delete("/delete/{id}")
async def delete_offer(id: int, db: Session = Depends(get_db)):
    offer = "offer"
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} not found",
        )
    # offers_dict.pop(id)
    # print(offers_dict)

    return {"Offer deleted": id}


