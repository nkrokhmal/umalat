import os

os.environ["environment"] = "interactive"
from app.schedule_maker.models import cast_model
from app.models import *

from app.schedule_maker.departments.mascarpone.algo.mascarpone_boilings import *


def test_make_mascarpone_boiling():
    sku = cast_model(MascarponeSKU, 82)
    values = [[0, sku, 10]]
    boiling_group_df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])

    print(make_mascorpone_boiling(boiling_group_df))


def test_make_mascarpone_boiling_group():
    sku = cast_model(MascarponeSKU, 82)
    values = [[0, sku, 10]]
    boiling_group_df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])

    print(make_mascarpone_boiling_group(boiling_group_df, boiling_group_df))


if __name__ == "__main__":
    test_make_mascarpone_boiling()
    test_make_mascarpone_boiling_group()
