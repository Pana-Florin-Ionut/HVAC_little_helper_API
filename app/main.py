import random
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel

offers_dict = {
    1: {
        "offer_name": "Offer 1",
        "items": {
            "1": ["Elbow", "500", "333", "44", "buc", "31"],
            "2": ["Tube", "300", "49", "ml", "15"],
        },
    },
    2: {
        "offer_name": "Offer 2",
        "items": {
            "1": ["Elbow", "500", "333", "44", "buc", "31"],
            "2": ["Tube", "300", "49", "ml", "15"],
            "3": ["Tube", "300", "49", "ml", "15"],
        },
    },
    3: {
        "offer_name": "Offer 3",
        "items": {
            "1": ["Elbow", "1500", "3313", "44", "buc", "31"],
            "2": ["Tube", "3100", "419", "ml", "15"],
            "3": ["Tube", "1300", "491", "ml", "15"],
        },
    },
}


def find_offer(id):
    return offers_dict.get(id)


app = FastAPI()


class Offer(BaseModel):
    offer_name: str
    items: dict


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/offers")
async def offers():
    return {"message": "Here are your offers"}


@app.post("/offers", status_code=status.HTTP_201_CREATED)
async def create_offer(offer: Offer):
    id = random.randint(0, 10000000)
    offers_dict[id] = offer.dict()
    # print(offer)
    # print(offer.dict())
    print(offers_dict)
    return {"New offer created": offer.offer_name}


@app.get("/offers/{id}")
async def get_offer(id: int):
    offer = find_offer(id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} not found",
        )
    return offer


@app.delete("/delete/{id}")
async def delete_offer(id: int):
    offer = find_offer(id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} not found",
        )
    offers_dict.pop(id)
    print(offers_dict)

    return {"Offer deleted": id}
