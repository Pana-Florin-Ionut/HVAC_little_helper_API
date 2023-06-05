from fastapi.testclient import TestClient
import pytest
from app.database import get_db
from app.main import app
from app.oauth2 import create_access_token
from app import schemas, table_models_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("DBPASS")
user = os.getenv("DBUSER")
host = os.getenv("DBHOST")
name = os.getenv("TESTDBNAME")
port = os.getenv("DBPORT")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# client = TestClient(app)
@pytest.fixture()
def session():
    table_models_required.Base.metadata.drop_all(bind=engine)
    table_models_required.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    # Code that run before test run
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    # Code that run after test run


@pytest.fixture()
def test_user_1(client):
    user_data = {
        "email": "ionut@test.com",
        "password": "123456",
        "role": "application_administrator",
    }
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user_1):
    return create_access_token({"user_id": test_user_1["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_companies_1(test_user_1, session):
    company_data = [
        {
            "company_name": "test_company_1",
            "company_key": "TC1",
        },
        {
            "company_name": "test_company_2",
            "company_key": "TC2",
        },
        {
            "company_name": "test_company_3",
            "company_key": "TC3",
        },
    ]

    def create_companies(company):
        return table_models_required.Companies(**company)

    company_map = list(map(create_companies, company_data))
    session.add_all(company_map)
    session.commit()


# @pytest.fixture
# def test_offers(test_user_1, session):
#     offer_data = [
#         {
#             "client_id": test_user_1["id"],
#             "company_id": 1,
#             "project_id": 1,
#             "offer_name": "test_offer_1",
#             "offer_key": "TO1",
#             "is_finalized": False,
#         },
#         {
#             "client_id": test_user_1["id"],
#             "company_id": 1,
#             "project_id": 1,
#             "offer_name": "test_offer_2",
#             "offer_key": "TO2",
#             "is_finalized": False,
#         },
#         {
#             "client_id": test_user_1["id"],
#             "company_id": 1,
#             "project_id": 1,
#             "offer_name": "test_offer_3",
#             "offer_key": "TO3",
#             "is_finalized": False,
#         },
#     ]
#     def create_offer(offer):
#         return schemas.Offer(**offer)

#     offer_map = list(map(create_offer, offer_data))
#     session.add_all(offer_map)
#     session.commit()


# #    client_id: int | None = None
# #     company_id: int
# #     project_id: int
# #     offer_name: str
# #     offer_key: str
# #     is_finalized: bool = False
