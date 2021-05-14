import pytest
import os


@pytest.fixture()
def use_interactive_environment():
    os.environ["environment"] = "interactive"
