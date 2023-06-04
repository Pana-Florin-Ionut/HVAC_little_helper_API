import pytest
from app import schemas
# from .database import client, session  # do not delete
from dotenv import load_dotenv
import os
from jose import jwt

load_dotenv()


# example
# def test_test(client, session):
#     session.add(table_models_required.User(email="XXXXXXXXXXXXXXXX", password="123456"))
#     session.commit()
#     response = client.get("/test")
#     assert response.status_code == 200


def test_create_user(client):
    response = client.post(
        "/users/", json={"email": "ionut@email.com", "password": "123456"}
    )
    new_user = schemas.UserOut(**response.json())
    assert response.status_code == 201
    assert new_user.email == "ionut@email.com"
    # assert response.json().get("password") == "XXXXXXXXXXXXX"


def test_login_user(client, test_user_1):
    res = client.post(
        "/login",
        data={"username": test_user_1["email"], "password": test_user_1["password"]},
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, os.getenv("SECRET_KEY"), algorithms = os.getenv("ALGORITHM"))
    id = payload.get("user_id")
    assert id == test_user_1["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
