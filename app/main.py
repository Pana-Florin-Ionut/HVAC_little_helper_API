from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from . import table_models_optional
from .database import engine, get_db
from . import tables
from .database_model import Database as db
from . import schemas
from .database_connection import conn
from typing import List
from .routers import companies, projects, users, offers
from . import table_models_required


# class Offer(BaseModel):

db = db(conn)

table_models_required.Base.metadata.create_all(bind=engine)


offers_table = "offers"


app = FastAPI()

app.include_router(projects.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(offers.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/offers",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.OffersRetrieve],
)
async def offers(db: Session = Depends(get_db)):
    offers = db.query(table_models_required.Offers).all()
    return offers


@app.post(
    "/offers/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.OffersRetrieve,
)
async def create_offer(offer: schemas.OffersCreate, db: Session = Depends(get_db)):
    new_offer = table_models_required.Offers(**offer.dict())
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


@app.get("/offers/{id}")
async def get_offer(id: int):
    print(offer)
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


def create_new_offer_table(title):
    table_models_optional.create_offer_table(engine, title)


@app.post("/offer/{offer_name}")
def create_offer(
    offer: schemas.Offers,
):
    # database_connection.execute_query2(query)
    try:
        query = tables.make_table(offer.offer_name)
        db.create_table(query)
        # return {f"{offer}": f"{offer_name}"}
        return {"message": f"{offer.offer_name} created"}
    except Exception as e:
        print(e)
        return {"message": e}


@app.get("/offer/{offer_name}")
def get_offer(
    offer_name,
):
    offer = db.get_table(f"SELECT * FROM {offer_name}")
