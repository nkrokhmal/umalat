from tests.conftest import client


def test_empty_db(client):
    with client.test_client() as client:
        response = client.get('/')

        assert response.status_code == 200
