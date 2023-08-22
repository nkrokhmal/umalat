import math

import pandas as pd

from app.utils.features.merge_boiling_utils import Boilings
from app.utils.mascarpone.order import CREAM_CHEESE_ORDER, CREAM_ORDER, MASCARPONE_ORDER, Order


def add_fields(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        df.rename({"plan": "kg"}, axis="columns", inplace=True)
        df["name"] = df["sku"].apply(lambda sku: sku.name)
        df["boiling_type"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0].to_str())
        df["output"] = df["max_boiling_weight"]
        df["coeff"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0].output_coeff)

        return df[
            [
                "id",
                "group",
                "output",
                "name",
                "boiling_type",
                "kg",
            ]
        ]

    return df


def mascarpone_boiling_plan_create(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df[["group", "form_factor"]] = df["sku"].apply(lambda x: pd.Series([x.group.name, x.form_factor.name]))

    boiling_lambda = lambda x: pd.Series([x.weight_netto, x.percent, x.is_lactose, x.flavoring_agent, x.output_kg])
    df[["weight", "percent", "is_lactose", "flavoring_agent", "output_kg"]] = df["sku"].apply(
        lambda x: boiling_lambda(x.made_from_boilings[0])
    )

    return (
        handle_group(df, "Маскарпоне", MASCARPONE_ORDER),
        handle_group(df, "Кремчиз", CREAM_CHEESE_ORDER),
        handle_group(df, "Сливки", CREAM_ORDER),
    )


def proceed_order(order: Order, df: pd.DataFrame, boilings: Boilings) -> Boilings:
    df_filter = df[df.apply(lambda row: order.order_filter(row), axis=1)]

    if not df_filter.empty:
        df_filter_groups = [group for _, group in df_filter.groupby("boiling_id")]

        for df_filter_group in sorted(df_filter_groups, key=lambda x: x["weight"].iloc[0], reverse=True):
            df_group_dict = df_filter_group.to_dict("records")

            boilings.add_group(
                df_group_dict,
            )
    return boilings


def handle_group(df: pd.DataFrame, group: str, orders: list[Order]) -> pd.DataFrame:
    output_tons: list[float | int] = [df[df["group"] == group]["output_kg"].iloc[0]]
    boilings_iterator = Boilings(max_iter_weight=output_tons)

    for order in orders:
        boilings_iterator = proceed_order(order, df, boilings_iterator)
    boilings_iterator.finish()
    return add_fields(pd.DataFrame(boilings_iterator.boilings))
