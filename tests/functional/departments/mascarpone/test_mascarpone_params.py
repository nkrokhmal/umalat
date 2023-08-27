from pathlib import Path

import flask
import pandas as pd

from pytest import fixture

from app.globals import db
from app.main.params.download_mascarpone import get_mascarpone_parameters
from app.models import Department, Washer
from app.models.fill_db.fill_mascarpone import validate_params
from tests.conftest import client


MASCARPONE_TEST_DIR: Path = Path("app/data/tests/mascarpone")


@fixture(scope="module")
def df_parameters() -> pd.DataFrame:
    return pd.read_excel(MASCARPONE_TEST_DIR / "parameters.xlsx", index_col=0).fillna("")


@fixture(scope="module")
def df_parameters_corrupted() -> pd.DataFrame:
    return pd.read_excel(MASCARPONE_TEST_DIR / "parameters_corrupted.xlsx", index_col=0).fillna("")


def test_get_mascarpone_parameters(df_parameters: pd.DataFrame) -> None:
    df = get_mascarpone_parameters()
    assert df.equals(df_parameters)


def test_validate_mascarpone_parameters(df_parameters_corrupted: pd.DataFrame) -> None:
    is_valid, msg = validate_params(df_parameters_corrupted)
    assert not is_valid
    assert (
        msg == "Технология Линия Маскарпоне, Маскарпоне, 0.2 кг, 80, ,  имеет разные параметры. Проверьте строки 13 и 0"
    )


def test_mascarpone_get_washer(client: flask.Flask) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.mascarpone_get_washer", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_mascarpone_edit_washer(client: flask.Flask) -> None:
    with client.test_client() as client:
        washer = db.session.query(Washer).join(Washer.department).filter(Department.name == "Маскарпоновый цех").first()
        url = flask.url_for("main.mascarpone_edit_washer", washer_id=washer.id, _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_mascarpone_download_params(client: flask.Flask, df_parameters: pd.DataFrame) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.download_mascarpone", _external=False)

        response = client.post(url, follow_redirects=True)
        assert response.status_code == 200

        df = pd.read_excel(response.data)
        df.set_index(df.columns[0], inplace=True)
        df.fillna("", inplace=True)
        assert df.equals(df_parameters)
