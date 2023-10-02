import io

import flask

from tests.conftest import client


def test_ricotta_get_schedule(client: flask.Flask) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.ricotta_schedule", _external=False)
        response = client.get(url)
        assert response.status_code == 200


# def test_ricotta_post_schedule(client):
#     filepath = client.config["TEST_RICOTTA"]
#     department_name = "Рикоттный цех"
#     BatchNumber.remove_department_batches(department_name)
#
#     with client.test_client() as client:
#         url = url_for("main.ricotta_schedule", _external=False)
#         data = {"date": "2021-01-01", "batch_number": 1, "beg_time": "07:00", "submit": "submit"}
#         with open(filepath, "rb") as f:
#             data["input_file"] = (io.BytesIO(f.read()), "ricotta.xlsx")
#         response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
#         new_last_batch = BatchNumber.last_batch_department(department_name)
#         try:
#             assert response.status_code == 200
#             assert 0 < new_last_batch
#         finally:
#             BatchNumber.remove_department_batches(department_name)
