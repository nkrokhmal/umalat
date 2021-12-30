import io
from tests.conftest import client
from flask import url_for


def test_butter_get_boiling_plan(client):
    with client.test_client() as client:
        url = url_for("main.butter_boiling_plan", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_butter_post_boiling_plan(client):
    filepath = client.config["TEST_BUTTER"]
    with client.test_client() as client:
        url = url_for("main.butter_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, 'rb') as f:
            data['input_file'] = (io.BytesIO(f.read()), "butter.xlsx")
        response = client.post(
            url, data=data, follow_redirects=True, content_type='multipart/form-data'
        )
        assert response.status_code == 200


def test_butter_post_boiling_plan_csv(client):
    filepath = client.config["TEST_BOILING_CSV"]
    with client.test_client() as client:
        url = url_for("main.butter_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, 'rb') as f:
            data['input_file'] = (io.BytesIO(f.read()), "test_boiling.csv")
        response = client.post(
            url, data=data, follow_redirects=True, content_type='multipart/form-data'
        )
        assert response.status_code == 200


def test_butter_post_boiling_plan_excel(client):
    filepath = client.config["TEST_BOILING_NEW_FORMAT"]
    with client.test_client() as client:
        url = url_for("main.butter_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, 'rb') as f:
            data['input_file'] = (io.BytesIO(f.read()), "test_boiling.xlsx")
        response = client.post(
            url, data=data, follow_redirects=True, content_type='multipart/form-data'
        )
        assert response.status_code == 200