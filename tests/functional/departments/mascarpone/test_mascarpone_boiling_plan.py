import io
import flask
import pytest

from pathlib import Path

import pytest

from tests.conftest import client


MASCARPONE_TEST_DIR: Path = Path("app/data/tests/mascarpone")


def test_mascarpone_get_boiling_plan(client):
    with client.test_client() as client:
        url = flask.url_for("main.mascarpone_boiling_plan", _external=False)
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.parametrize("filename", ["leftovers.xlsx", "leftovers.csv"])
def test_mascarpone_post_boiling_plan(client: flask.Flask, filename: str) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.mascarpone_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(MASCARPONE_TEST_DIR / filename, "rb") as f:
            data["input_file"] = (io.BytesIO(f.read()), filename)
        response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
        assert response.status_code == 200


