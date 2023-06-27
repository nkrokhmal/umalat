import io
import glob
from tests.conftest import client
from app.imports.runtime import *
from app.models import *
from flask import url_for


def test_mozzarella_schedule_stress(client):
    paths = glob.glob(f"{client.config['TEST_STRESS_MOZZARELLA']}/*.xlsx")
    with client.test_client() as client:
        for filepath in paths:
            department_name = "Моцарельный цех"
            BatchNumber.remove_department_batches(department_name)

            url = url_for("main.mozzarella_schedule", _external=False)
            data = {
                "date": "2021-01-01",
                "add_full_boiling": True,
                "batch_number": 1,
                "water_beg_time": "07:00",
                "salt_beg_time": "07:00",
                "submit": "submit"
            }
            with open(filepath, 'rb') as f:
                data['input_file'] = (io.BytesIO(f.read()), "mozzarella.xlsx")
            response = client.post(
                url, data=data, follow_redirects=True, content_type='multipart/form-data'
            )
            new_last_batch = BatchNumber.last_batch_department(department_name)
            try:
                assert response.status_code == 200, f"Exception in file {filepath}"
                assert 0 < new_last_batch
            finally:
                BatchNumber.remove_department_batches(department_name)