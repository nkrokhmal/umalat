import io

from flask import url_for

from tests.conftest import client


def test_ricotta_get_boiling_plan(client):
    with client.test_client() as client:
        url = url_for("main.ricotta_boiling_plan", _external=False)
        response = client.get(url)
        assert response.status_code == 200


def test_ricotta_post_boiling_plan(client):
    filepath = client.config["TEST_RICOTTA"]
    with client.test_client() as client:
        url = url_for("main.ricotta_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, "rb") as f:
            data["input_file"] = (io.BytesIO(f.read()), "ricotta.xlsx")
        response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
        assert response.status_code == 200


"""
                sku    plan  boiling_id  sku_id
0    <RicottaSKU 2>   192.0           2       2
3    <RicottaSKU 3>   439.0           3       3
4   <RicottaSKU 18>  1691.0           3      18
7   <RicottaSKU 27>    54.0           3      27
10  <RicottaSKU 13>    96.0           4      13
11   <RicottaSKU 4>  6629.0           4       4
14   <RicottaSKU 7>    11.0           5       7
18   <RicottaSKU 8>    20.0           6       8
19  <RicottaSKU 11>    18.0           6      11
22  <RicottaSKU 10>   435.0           7      10
23  <RicottaSKU 28>    80.0           7      28
26  <RicottaSKU 16>   143.0          10      16
29  <RicottaSKU 17>    89.0          11      17
32  <RicottaSKU 24>  2382.0          15      24
35  <RicottaSKU 25>   276.0          16      25

"""


def test_ricotta_post_boiling_plan_csv(client):
    filepath = client.config["TEST_BOILING_CSV"]
    with client.test_client() as client:
        url = url_for("main.ricotta_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, "rb") as f:
            data["input_file"] = (io.BytesIO(f.read()), "test_boiling.csv")
        response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
        assert response.status_code == 200


def test_ricotta_post_boiling_plan_new(client):
    filepath = client.config["TEST_BOILING_NEW_FORMAT"]
    with client.test_client() as client:
        url = url_for("main.ricotta_boiling_plan", _external=False)
        data = {"date": "2021-01-01", "submit": "submit"}
        with open(filepath, "rb") as f:
            data["input_file"] = (io.BytesIO(f.read()), "test_boiling.xlsx")
        response = client.post(url, data=data, follow_redirects=True, content_type="multipart/form-data")
        assert response.status_code == 200
