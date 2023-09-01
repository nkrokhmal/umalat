import os

import flask


os.environ["APP_ENVIRONMENT"] = "runtime"

import pytest

from app.app import create_app


@pytest.fixture
def client() -> flask.Flask:
    app, rq = create_app("test")
    app.config["LOGIN_DISABLED"] = True
    return app
    # with app.test_client() as client:
    #     yield client


@pytest.fixture(autouse=True)
def _push_request_context(request, client):
    ctx = client.test_request_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
