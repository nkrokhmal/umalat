import io
from tests.conftest import client
from flask import url_for
from app.imports.runtime import *
from io import StringIO


def test_mascarpone_download_params(client):
    params_df = pd.read_excel(r'app/data/static/params/mascarpone_test.xlsx')
    with client.test_client() as client:
        url = url_for("main.download_mascarpone", _external=False)
        response = client.post(url, follow_redirects=True)
        df = pd.read_excel(response.data)

        df = df.reindex(sorted(df.columns), axis=1)
        params_df = params_df.reindex(sorted(df.columns), axis=1)

        assert sorted(df.columns) == sorted(params_df.columns)
        assert df.equals(params_df)
        assert response.status_code == 200