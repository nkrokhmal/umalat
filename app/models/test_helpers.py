import os

os.environ["environment"] = "interactive"

from app.models import *


def test_models():
    print(cast_model(MozzarellaSKU, 1))
    print(cast_model(MozzarellaSKU, "1.0"))
    print(cast_mozarella_boiling(1))
    print(cast_mozarella_form_factor(1))


if __name__ == "__main__":
    test_models()
