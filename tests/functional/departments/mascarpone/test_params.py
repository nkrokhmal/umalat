import io
import flask
import pandas as pd

from pathlib import Path
from pytest import fixture

from app.enum import DepartmentName
from app.globals import db
from app.main.params.download_mascarpone import get_mascarpone_parameters
from app.models import Department, MascarponeBoiling, MascarponeBoilingTechnology, MascarponeSKU, Washer
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
    assert (df == df_parameters).all().all()


def test_validate_mascarpone_parameters(df_parameters_corrupted: pd.DataFrame) -> None:
    is_valid, msg = validate_params(df_parameters_corrupted)
    assert not is_valid
    assert (
        msg == "Технология Линия Маскарпоне, Маскарпоне, 0.2 кг, 80, ,  имеет разные параметры. Проверьте строки 13 и 0"
    )


def test_mascarpone_download_params(client: flask.Flask, df_parameters: pd.DataFrame) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.download_mascarpone", _external=False)

        response = client.post(url, follow_redirects=True)
        assert response.status_code == 200

        df = pd.read_excel(response.data)
        df.set_index(df.columns[0], inplace=True)
        df.fillna("", inplace=True)
        assert df.equals(df_parameters)


def test_mascarpone_upload_params(client: flask.Flask, df_parameters: pd.DataFrame) -> None:
    body: dict = {}
    with open(MASCARPONE_TEST_DIR / "parameters.xlsx", "rb") as f:
        body["input_file"] = (io.BytesIO(f.read()), "mascarpone.xlsx")

    update_url = flask.url_for("main.mascarpone_update_params", _external=False)
    download_url = flask.url_for("main.download_mascarpone", _external=False)

    with client.test_client() as client:
        response = client.post(update_url, data=body, follow_redirects=True, content_type="multipart/form-data")
        assert response.status_code == 200

        response = client.post(download_url, follow_redirects=True)
        assert response.status_code == 200

        df = pd.read_excel(response.data)
        df.set_index(df.columns[0], inplace=True)
        df.fillna("", inplace=True)
        assert df.equals(df_parameters)


def test_mascarpone_get_params(client: flask.Flask) -> None:
    urls: list[str] = [
        flask.url_for("main.mascarpone_get_washer", _external=False),
        flask.url_for("main.mascarpone_get_boiling", _external=False),
        flask.url_for("main.mascarpone_get_sku", _external=False, page=1),
        flask.url_for("main.mascarpone_get_boiling_technology", _external=False),
    ]

    with client.test_client() as client:
        for url in urls:
            response = client.get(url)
            assert response.status_code == 200


def test_mascarpone_edit_params(
    client: flask.Flask,
) -> None:
    with client.test_client() as client:
        washer = (
            db.session.query(Washer)
            .join(Washer.department)
            .filter(Department.name == DepartmentName.MASCARPONE)
            .first()
        )
        sku = db.session.query(MascarponeSKU).first()
        boiling = db.session.query(MascarponeBoiling).first()
        boiling_technology = db.session.query(MascarponeBoilingTechnology).first()
        urls: list[str] = [
            flask.url_for(endpoint="main.mascarpone_edit_washer", washer_id=washer.id, _external=False),
            flask.url_for(endpoint="main.mascarpone_edit_boiling", boiling_id=boiling.id, _external=False),
            flask.url_for(endpoint="main.mascarpone_edit_sku", sku_id=sku.id, _external=False),
            flask.url_for(
                endpoint="main.mascarpone_edit_boiling_technology",
                boiling_technology_id=boiling_technology.id,
                _external=False,
            ),
        ]
        for url in urls:
            response = client.get(url)
            assert response.status_code == 200
