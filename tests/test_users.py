from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
    assert response.json().get("message") == "Hello World"