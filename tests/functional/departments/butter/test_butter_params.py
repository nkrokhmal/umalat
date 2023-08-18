import io

from io import StringIO

from flask import url_for

from app.imports.runtime import *
from tests.conftest import client


def test_butter_download_params(client):
    params_df = pd.read_excel(r"app/data/static/params/butter_test.xlsx")
    with client.test_client() as client:
        url = url_for("main.download_butter", _external=False)
        response = client.post(url, follow_redirects=True)
        df = pd.read_excel(response.data)

        df = df.reindex(sorted(df.columns), axis=1)
        params_df = params_df.reindex(sorted(df.columns), axis=1)

        assert sorted(df.columns) == sorted(params_df.columns)
        assert df.equals(params_df)
        assert response.status_code == 200
