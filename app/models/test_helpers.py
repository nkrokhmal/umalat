import os

os.environ["APP_ENVIRONMENT"] = "interactive"

from app.models import *


def test_models():
    print(cast_model(MozzarellaSKU, 1))
    print(cast_model(MozzarellaSKU, "1.0"))
    print(cast_mozzarella_boiling(1))
    print(cast_mozzarella_form_factor(1))


if __name__ == "__main__":
    test_models()
