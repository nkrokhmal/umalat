import pandas as pd

from app.utils.mascarpone.order import CREAM_CHEESE_ORDER, CREAM_ORDER, MASCARPONE_ORDER, Order
from app.utils.mascarpone.utils import BoilingsHandler


def add_fields(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        df.rename({"plan": "kg"}, axis="columns", inplace=True)
        df["name"] = df["sku"].apply(lambda sku: sku.name)
        df["boiling_type"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0].to_str())
        df["output"] = df["output_kg"]
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
        handle_group(df, MASCARPONE_ORDER),
        handle_group(df, CREAM_CHEESE_ORDER),
        handle_group(df, CREAM_ORDER),
    )


def handle_group(df: pd.DataFrame, orders: list[Order]) -> pd.DataFrame:
    handler = BoilingsHandler()

    for order in orders:
        df_order = df[df.apply(lambda row: order.order_filter(row), axis=1)]

        if not df_order.empty:
            groups = [group for _, group in df_order.groupby("boiling_id")]

            for group in sorted(groups, key=lambda x: x["weight"].iloc[0], reverse=True):
                group_dict = group.to_dict("records")
                max_weight = group_dict[0]["output_kg"]

                handler.handle_group(group_dict, max_weight=max_weight)

    return add_fields(pd.DataFrame(handler.boiling_groups))
