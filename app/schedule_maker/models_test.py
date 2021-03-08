import os

os.environ["environment"] = "interactive"

from app.schedule_maker.models import *


def test_models():
    print(cast_sku(1))
    print(cast_sku("1.0"))
    print(cast_mozarella_boiling(1))
    print(cast_mozarella_boiling("salt, 2.7, Альче"))
    print(cast_mozarella_form_factor(1))


if __name__ == "__main__":
    test_models()
