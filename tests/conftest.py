from fastapi.testclient import TestClient
import pytest
from app.database import get_db
from app.main import app
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
    user_data = {"email": "ionut@test.com", "password": "123456"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user
