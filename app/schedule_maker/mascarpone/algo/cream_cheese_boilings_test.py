import os

os.environ["environment"] = "interactive"
from app.schedule_maker.models import cast_model
from app.models import *

from app.schedule_maker.mascarpone.algo.cream_cheese_boilings import *


def test_make_mascarpone_boiling():
    sku = cast_model(CreamCheeseSKU, 93)
    values = [[0, sku, 10]]
    boiling_group_df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])

    print(make_cream_cheese_boiling(boiling_group_df))


if __name__ == "__main__":
    test_make_mascarpone_boiling()
