import pytest
from flask import template_rendered
from app.app import create_app


@pytest.fixture
def client():
    app = create_app("test")
    with app.test_client() as client:
        yield client
