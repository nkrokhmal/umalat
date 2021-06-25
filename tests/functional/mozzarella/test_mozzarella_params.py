import io
from tests.conftest import client
from flask import url_for


# def test_mozzarella_params(client):
#     with client.test_client() as client:
#         url = url_for("main.mozzarella_params", _external=False)
#         response = client.get(url)
#         assert response.status_code == 200
#
#
# def test_mozzarella_add_sku(client):
#     with client.test_client() as client:
#         url = url_for("main.mozzarella_add_sku", _external=False)
#         response = client.get(url)
#         assert response.status_code == 200
#
#
# def test_mozzarella_copy_sku(client):
#     with client.test_client() as client:
#         mozzarella_id = 41
#         url = url_for(f"main.mozzarella_add_sku/{mozzarella_id}", _external=False)
#         response = client.get(url)
#         assert response.status_code == 200




