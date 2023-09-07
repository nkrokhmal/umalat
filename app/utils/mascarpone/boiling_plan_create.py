import pandas as pd

from app.utils.mascarpone.order import CREAM_CHEESE_ORDER, CREAM_ORDER, MASCARPONE_ORDER, Order
from app.utils.mascarpone.utils import MascarponeBoilingsHandler


def add_fields(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        df.rename({"plan": "kg"}, axis="columns", inplace=True)
        df["name"] = df["sku"].apply(lambda sku: sku.name)
        df["line"] = df["sku"].apply(lambda sku: sku.line.name)
        df["boiling_type"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0].to_str())
        df["coeff"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0].output_coeff)

        return df[
            [
                "id",
                "sku",
                "group",
                "name",
                "boiling_type",
                "line",
                "kg",
                "total_input_kg",
            ]
        ]

    return df


def mascarpone_boiling_plan_create(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df[["group", "form_factor"]] = df["sku"].apply(lambda x: pd.Series([x.group.name, x.form_factor.name]))

    boiling_lambda = lambda x: pd.Series([x.weight_netto, x.percent, x.is_lactose, x.flavoring_agent])
    df[["weight", "percent", "is_lactose", "flavoring_agent"]] = df["sku"].apply(
        lambda x: boiling_lambda(x.made_from_boilings[0])
    )

    return (
        handle_group(df, MASCARPONE_ORDER),
        handle_group(df, CREAM_CHEESE_ORDER),
        handle_group(df, CREAM_ORDER),
    )


def handle_group(df: pd.DataFrame, orders: list[Order]) -> pd.DataFrame:
    handler = MascarponeBoilingsHandler()

    for order in orders:
        df_order = df[df.apply(lambda row: order.order_filter(row), axis=1)]
        df_order["total_input_kg"] = order.max_weight

        if not df_order.empty:
            groups = [group for _, group in df_order.groupby("boiling_id")]

            for group in sorted(groups, key=lambda x: x["weight"].iloc[0], reverse=True):
                group_dict = group.to_dict("records")
                max_weight = order.max_weight

                handler.handle_group(group_dict, max_weight=max_weight)

    return add_fields(pd.DataFrame(handler.boiling_groups))
