import random
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import table_models_required, table_models_optional
from .database import engine, get_db
from . import tables
from .database_model import Database as db
from . import db_test
from .database_connection import conn
from pydantic import parse_obj_as
from typing import List

db = db(conn)

# table_models_required.Base.metadata.create_all(bind=engine)

offers_table = "offers"

# try:
#     conn = psycopg2.connect(
#         host="localhost",
#         database="HLH_first",
#         user="postgres",
#         password="123456tyTY",
#         cursor_factory=RealDictCursor,
#     )
#     cursor = conn.cursor()
#     print("Database connection was successful")
# except Exception as error:
#     print("Database connection was failed")
#     print("Error: ", error)
db.create_table(tables.create_clients_table())
db.create_table(tables.create_projects_table())
db.create_table(tables.create_offers_table())
# db.create_table(tables.create_products_table())


def find_offer(id):
    return {"message": "offers"}


app = FastAPI()


@app.get("/", response_model=List[db_test.OffersRetrieve])
async def root(get_db: Session = Depends(get_db), response = db_test.OffersRetrieve):
    # print(list(get_db.execute(tables.get_offers())))
    response = get_db.execute(tables.get_offers())
    response_dict = response.mappings().all() #get response as a list of dictionaries
    # print(response_dict)
    # for r in response_dict:
    #     print(db_test.OffersRetrieve(**r))
    # offers = []
    # for r in response:
    #     id = r[0]
    #     client_id = r[1]
    #     project_id = r[2]
    #     offer_name = r[3]
    #     new = db_test.OffersRetrieve(id=id, client_id=client_id, project_id=project_id, offer_name=offer_name)
    #     offers.append(new)
    #     # print(new)
    # return offers
    return response_dict


@app.get("/offers")
async def offers():
    return {"message": "Offers"}


@app.post(
    "/offers/",
    status_code=status.HTTP_201_CREATED,
    # response_model=db_test.OffersRetrieve,
)
async def create_offer(offer: db_test.OffersCreate):
    print(offer.offer_name)
    print(offer)
    print(offer.dict())
    offer_name = offer.offer_name
    offer_body = offer.dict()
    try:
        db.execute(
            tables.insert_offer_row(
                table_name=offers_table,
                columns=list(offer_body.keys()),
                values=offer_body.values(),
            )
        )
        # db.create_table(tables.create_offer_table(offer_name))
        return {"New offer entry": offer_name}
    except Exception as e:
        print(f"Error:  {e}")
        if (
            f'duplicate key value violates unique constraint "offers_offer_name_key"\nDETAIL:  Key (offer_name)=({offer_name}) already exists.\n'
            in str(e)
        ):
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Offer already exists"
            )
            # return {"message": "Offer already exists"}

        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad request")

    # print(offers_dict)


@app.get("/offers/{id}")
async def get_offer(id: int):
    offer = find_offer(id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} not found",
        )
    return offer


@app.put("/offers/{id}")
async def update_offer(id: int, offer: db_test.Offer):
    index = find_offer(id)
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
    offer = find_offer(id)
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
    offer: db_test.Offers,
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
