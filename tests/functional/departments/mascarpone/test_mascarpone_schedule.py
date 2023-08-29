from flask import url_for

from app.enum import DepartmentName
from app.imports.runtime import *
from app.models import *
from tests.conftest import client


def test_mascarpone_get_schedule(client):
    with client.test_client() as client:
        url = url_for("main.mascarpone_schedule", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_mascarpone_post_schedule(client):
    filepath = client.config["TEST_MASCARPONE"]
    BatchNumber.remove_department_batches(DepartmentName.MASCARPONE)

    with client.test_client() as client:
        url = url_for("main.mascarpone_schedule", _external=False)
        data = {
            "date": "2021-01-01",
            "mascarpone_batch_number": 1,
            "cream_cheese_batch_number": 1,
            "robiola_batch_number": 1,
            "cottage_cheese_batch_number": 1,
            "cream_batch_number": 1,
            "beg_time": "07:00",
            "submit": "submit",
        }
        with open(filepath, "rb") as f:
            data["input_file"] = (io.BytesIO(f.read()), "mascarpone.xlsx")
        response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
        new_last_batch = BatchNumber.last_batch_department(DepartmentName.MASCARPONE)
        try:
            assert response.status_code == 200
            assert 0 < new_last_batch
        finally:
            BatchNumber.remove_department_batches(DepartmentName.MASCARPONE)
