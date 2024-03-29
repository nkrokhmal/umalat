import pandas as pd

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester

from app.models import MascarponeSKU, cast_model


def test_make_mascarpone_boiling():
    lazy_tester.configure_function_path()

    sku = cast_model(MascarponeSKU, 'Маскарпоне "Pretto", 80%, 0,25 кг, пл/с')
    values = [[0, 0, sku.made_from_boilings[0], sku, 10, False, 1]]
    boiling_group_df = pd.DataFrame(
        values,
        columns=[
            "boiling_key",
            "boiling_id",
            "boiling",
            "sku",
            "kg",
            "is_cream",
            "sourdough",
        ],
    )

    lazy_tester.log(make_mascorpone_boiling(boiling_group_df))
    lazy_tester.assert_logs()


def test_make_mascarpone_boiling_group():
    lazy_tester.configure_function_path()
    sku = cast_model(MascarponeSKU, 'Маскарпоне "Pretto", 80%, 0,25 кг, пл/с')

    def _create_boiling_group_df(sourdough):
        values = [[0, 0, sku.made_from_boilings[0], sku, 10, False, sourdough]]
        return pd.DataFrame(
            values,
            columns=[
                "boiling_key",
                "boiling_id",
                "boiling",
                "sku",
                "kg",
                "is_cream",
                "sourdough",
            ],
        )

    lazy_tester.log(make_mascarpone_boiling_group([_create_boiling_group_df(1), _create_boiling_group_df(2)]))
    lazy_tester.assert_logs()


if __name__ == "__main__":
    test_make_mascarpone_boiling()
    test_make_mascarpone_boiling_group()
