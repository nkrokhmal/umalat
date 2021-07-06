import io
from tests.conftest import client
from flask import url_for
from app.imports.runtime import *
from app.models import MozzarellaSKU


def test_mozzarella_params(client):
    with client.test_client() as client:
        url = url_for("main.mozzarella_params", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_mozzarella_add_sku(client):
    with client.test_client() as client:
        url = url_for("main.mozzarella_add_sku", _external=False)
        response = client.get(url)
        assert response.status_code == 200





