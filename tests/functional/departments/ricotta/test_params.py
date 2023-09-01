from pathlib import Path

import flask
import pandas as pd

from pytest import fixture

from app.models.fill_db.fill_ricotta import RicottaFiller
from tests.conftest import client


RICOTTA_TEST_DIR: Path = Path("app/data/tests/ricotta")


@fixture(scope="module")
def filler() -> RicottaFiller:
    return RicottaFiller()


@fixture(scope="module")
def df_parameters() -> pd.DataFrame:
    return pd.read_excel(RICOTTA_TEST_DIR / "parameters.xlsx", index_col=0).fillna("")


@fixture(scope="module")
def df_parameters_corrupted() -> pd.DataFrame:
    return pd.read_excel(RICOTTA_TEST_DIR / "parameters_corrupted.xlsx", index_col=0).fillna("")


@fixture(scope="module")
def df_parameters_corrupted_weight() -> pd.DataFrame:
    return pd.read_excel(RICOTTA_TEST_DIR / "parameters_corrupted_weight.xlsx", index_col=0).fillna("")


def test_validate_ricotta_parameters(
    filler: RicottaFiller,
    df_parameters: pd.DataFrame,
    df_parameters_corrupted: pd.DataFrame,
    df_parameters_corrupted_weight: pd.DataFrame,
) -> None:
    msg = filler.validate_params(df_parameters)
    assert msg is None

    msg = filler.validate_params(df_parameters_corrupted)
    assert msg == f"Технологии варки с одинаковым именем имеют разные параметры. Проверьте строки 2 и 3"

    msg = filler.validate_params(df_parameters_corrupted_weight)
    assert msg == f"Некоторые SKU с одинаковыми параметрами имеют разный вход/выход. Проверьте строки 3 и 12"


def test_ricotta_download_params(client: flask.Flask, df_parameters: pd.DataFrame) -> None:
    with client.test_client() as client:
        url = flask.url_for("main.download_ricotta", _external=False)

        response = client.post(url, follow_redirects=True)
        assert response.status_code == 200

        df = pd.read_excel(response.data)
        df.set_index(df.columns[0], inplace=True)
        df.fillna("", inplace=True)
        assert df.equals(df_parameters)


#
#
# def test_ricotta_download_params(client):
#     params_df = pd.read_excel(r"app/data/static/params/ricotta_test.xlsx")
#     with client.test_client() as client:
#         url = url_for("main.download_ricotta", _external=False)
#         response = client.post(url, follow_redirects=True)
#         df = pd.read_excel(response.data)
#
#         df = df.reindex(sorted(df.columns), axis=1)
#         params_df = params_df.reindex(sorted(df.columns), axis=1)
#
#         assert sorted(df.columns) == sorted(params_df.columns)
#         assert df.equals(params_df)
#         assert response.status_code == 200
