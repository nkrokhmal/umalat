import io

from flask import url_for

from tests.conftest import client


def test_save_batches(client):
    with client.test_client() as client:
        url = url_for("main.save_batches", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_upload_batches(client):
    with client.test_client() as client:
        url = url_for("main.upload_batches", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_save_last_batches(client):
    with client.test_client() as client:
        url = url_for("main.save_last_batches", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_upload_last_batches(client):
    with client.test_client() as client:
        url = url_for("main.upload_last_batches", _external=False)
        response = client.get(url)
        assert response.status_code == 200
