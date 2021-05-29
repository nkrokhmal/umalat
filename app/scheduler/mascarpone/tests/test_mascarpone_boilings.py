from app.imports.runtime import *
from app.models import *

from app.scheduler.mascarpone.algo.mascarpone_boilings import *


def test_make_mascarpone_boiling():
    sku = cast_model(SKU, 90)
    values = [[0, 0, sku.made_from_boilings[0], sku, 10, True]]
    boiling_group_df = pd.DataFrame(
        values,
        columns=["boiling_key", "boiling_id", "boiling", "sku", "kg", "is_cream"],
    )

    print(make_mascorpone_boiling(boiling_group_df))


def test_make_mascarpone_boiling_group():
    utils.lazy_tester.set_function_logs_path()

    sku = cast_model(SKU, 92)
    print(sku.name)
    values = [[0, 0, sku.made_from_boilings[0], sku, 10, True]]
    boiling_group_df = pd.DataFrame(
        values,
        columns=["boiling_key", "boiling_id", "boiling", "sku", "kg", "is_cream"],
    )

    utils.lazy_tester.log(
        "Boiling group",
        boiling_group=make_mascarpone_boiling_group(
            [boiling_group_df, boiling_group_df]
        ),
    )
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    # test_make_mascarpone_boiling()
    test_make_mascarpone_boiling_group()
