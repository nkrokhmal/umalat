from tests.conftest import client
from flask import url_for


def test_get_boiling_plan(client):
    url = url_for(".boiling_plan", _external=False)
    print(url)

    response = client.get('/')

    assert response.status_code == 200
