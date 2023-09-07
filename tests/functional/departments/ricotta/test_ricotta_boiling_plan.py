import io

from pathlib import Path

import flask
import pytest

from tests.conftest import client


RICOTTA_TEST_DIR: Path = Path("app/data/tests/ricotta")


def test_ricotta_get_boiling_plan(client: flask.Flask) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.ricotta_boiling_plan", _external=False)
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.parametrize("filename", ["leftovers.csv", "leftovers.xlsx"])
def test_ricotta_post_boiling_plan_csv(client: flask.Flask, filename: str) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.ricotta_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(RICOTTA_TEST_DIR / filename, "rb") as f:
            data["input_file"] = (io.BytesIO(f.read()), filename)
        response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
        assert response.status_code == 200
