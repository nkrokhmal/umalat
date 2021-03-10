import os

os.environ["environment"] = "interactive"
from app.schedule_maker.models import cast_model
from app.models import *

from app.schedule_maker.departments.ricotta.algo.boilings import *


def test_make_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(make_boiling(boiling_model))


def test_make_boiling_sequence():
    sku = cast_model(RicottaSKU, 62)
    print(make_boiling_sequence(sku))


def test_make_boiling_group():
    sku = cast_model(RicottaSKU, 62)
    print(make_boiling_group(sku))


if __name__ == "__main__":
    test_make_boiling()
    test_make_boiling_sequence()
    test_make_boiling_group()
