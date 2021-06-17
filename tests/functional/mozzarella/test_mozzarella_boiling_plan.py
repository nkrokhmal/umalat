import io
from tests.conftest import client
from flask import url_for


def test_mozzarella_get_boiling_plan(client):
    with client.test_client() as client:
        url = url_for("main.mozzarella_boiling_plan", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_mozzarella_post_boiling_plan(client):
    filepath = client.config["TEST_MOZZARELLA"]
    with client.test_client() as client:
        url = url_for("main.mozzarella_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, 'rb') as f:
            data['input_file'] = (io.BytesIO(f.read()), "mozzarella.xlsx")
        response = client.post(
            url, data=data, follow_redirects=True, content_type='multipart/form-data'
        )
        assert response.status_code == 200