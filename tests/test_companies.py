# def test_create_companies(authorized_client):


def test_get_companies(authorized_client, test_companies_1):
    response = authorized_client.get('/companies/')
    print(response.json())
    assert response.status_code == 200
