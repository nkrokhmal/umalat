import os


os.environ["APP_ENVIRONMENT"] = "test"

from app.models import *


def test_models():
    for i in range(1, 1000):
        try:
            sku = cast_model(SKU, i)
            print(sku, sku.name)
        except Exception as e:
            if "Failed to fetch element" not in str(e):
                # unexpected error
                raise

            # found all
            break

    for i in range(1, 1000):
        try:
            boiling = cast_model(Boiling, i)
            print(boiling, getattr(boiling, "name", None))
        except Exception as e:
            if "Failed to fetch element" not in str(e):
                # unexpected error
                raise

            # found all
            break
    # print(cast_model(BrynzaSKU, 'Халуми для жарки «kλαssikós», 45%, 0,3 кг, к/к').made_from_boilings)


if __name__ == "__main__":
    test_models()
