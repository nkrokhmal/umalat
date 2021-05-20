import io
from tests.conftest import client
from flask import url_for


def test_ricotta_get_schedule(client):
    with client.test_client() as client:
        url = url_for("main.schedule", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_mozzarella_post_schedule(client):
    filepath = client.config["TEST_RICOTTA"]
    with client.test_client() as client:
        url = url_for("main.ricotta_schedule", _external=False)
        data = {
            "date": "2021-01-01",
            "batch_number": 1,
            "beg_time": "07:00",
            "submit": "submit"
        }
        with open(filepath, 'rb') as f:
            data['input_file'] = (io.BytesIO(f.read()), "ricotta.xlsx")
        response = client.post(
            url, data=data, follow_redirects=True, content_type='multipart/form-data'
        )
        assert response.status_code == 200