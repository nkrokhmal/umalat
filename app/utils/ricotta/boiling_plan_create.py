import math

import pandas as pd

from app.models.ricotta import RicottaBoiling
from app.utils.features.merge_boiling_utils import Boilings
from app.utils.ricotta.order import RICOTTA_ORDERS
from app.utils.ricotta.utils import RicottaBoilingsHandler


POPULAR_NAMES = {
    "0.2": 'Рикотта "Pretto", 45%, 0,2 кг, пл/с',
    "0.5": 'Рикотта "Pretto", 45%, 0,5 кг, пл/с',
}


def add_fields(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        df.rename({"plan": "kg"}, axis="columns", inplace=True)
        df["name"] = df["sku"].apply(lambda sku: sku.name)
        df["boiling_type"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0].to_str())
        df = df[
            [
                "id",
                "kg",
                "sku",
                "name",
                "boiling_type",
                "output_kg",
                "boiling_count",
            ]
        ]
    return df


def saturate_boiling(boiling: RicottaBoiling) -> pd.Series:
    return pd.Series([boiling.weight, boiling.percent, boiling.flavoring_agent, boiling.output_kg])


def boiling_plan_create(df: pd.DataFrame, request_kg: int = 0) -> pd.DataFrame:
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df[["weight", "percent", "flavoring_agent", "output_kg"]] = df["sku"].apply(
        lambda x: saturate_boiling(x.made_from_boilings[0])
    )

    result = handle_ricotta(df)
    return add_fields(result)


def handle_ricotta(df: pd.DataFrame) -> pd.DataFrame:
    handler = RicottaBoilingsHandler()

    for order in RICOTTA_ORDERS:
        df_order = df[df.apply(lambda row: order.order_filter(row), axis=1)]

        if not df_order.empty:
            groups = [group for _, group in df_order.groupby("boiling_id")]

            for group in sorted(groups, key=lambda x: x["weight"].iloc[0], reverse=True):
                group_dict = group.to_dict("records")
                max_weight = group_dict[0]["output_kg"]

                handler.handle_group(group_dict, max_weight=max_weight)

    return pd.DataFrame(handler.boiling_groups)
