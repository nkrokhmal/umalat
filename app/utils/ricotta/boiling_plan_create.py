import pandas as pd

from app.models.ricotta import RicottaBoiling
from app.utils.features.merge_boiling_utils import Boilings
from app.utils.ricotta.order import RICOTTA_ORDERS, Order


POPULAR_NAMES = {
    "0.2": 'Рикотта "Pretto", 45%, 0,2 кг, пл/с',
    "0.5": 'Рикотта "Pretto", 45%, 0,5 кг, пл/с',
}


def boiling_plan_create(df: pd.DataFrame, request_kg: int = 0) -> pd.DataFrame:
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["flavoring_agent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].flavoring_agent)
    df["short_display_name"] = df["sku"].apply(lambda x: x.made_from_boilings[0].short_display_name)
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)

    result, boiling_number = handle_ricotta(df, request_kg=request_kg)

    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["output"] = result["output_per_tank"] * result["number_of_tanks"]
    result["boiling_type"] = result["sku"].apply(lambda sku: sku.made_from_boilings[0].to_str())
    result = result[
        [
            "id",
            "sku",
            "number_of_tanks",
            "group",
            "output",
            "name",
            "boiling_type",
            "kg",
            "boiling_count",
        ]
    ]
    result = group_result(result)
    return result


def group_result(df):
    agg = {
        "id": "first",
        "sku": "first",
        "number_of_tanks": "sum",
        "group": "first",
        "output": "first",
        "boiling_type": "first",
        "kg": "sum",
        "boiling_count": "sum",
    }
    df["number_of_tanks"] = df["boiling_count"].apply(lambda x: math.floor(x)) * df["sku"].apply(
        lambda x: x.made_from_boilings[0].number_of_tanks
    )

    return df.groupby("name", as_index=False).agg(agg).sort_values(by="id")


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

    return add_fields(pd.DataFrame(handler.boiling_groups))


def handle_order(order: Order, df: pd.DataFrame, boilings_ricotta, boilings_count=1):
    df_order = df[df.apply(lambda row: order.order_filter(row), axis=1)]

    if not df_order.empty:
        df_filter["output"] = df_filter["number_of_tanks"] * df_filter["output_per_tank"]
        df_filter["output"] = df_filter["output"].apply(lambda x: int(x))

        # df_filter_groups = [group for _, group in df_filter.groupby("output")]
        df_filter_groups = [group for _, group in df_filter.groupby(["sku_id"])]
        for df_filter_group in df_filter_groups:
            boilings_ricotta.init_iterator(df_filter_group["output"].iloc[0])
            boilings_ricotta.add_group(
                df_filter_group.to_dict("records"),
                boilings_count=boilings_count,
            )
    return boilings_ricotta


def handle_ricotta(df, request_ton=0):
    boilings_ricotta = Boilings()
    input_ton = db.session.query(RicottaLine).first().input_ton

    for order in RICOTTA_ORDER:
        boilings_ricotta = proceed_order(order, df, boilings_ricotta)

    boilings_ricotta.finish()
    sum_ton = pd.DataFrame(boilings_ricotta.boilings).groupby("id").first()["number_of_tanks"].sum() * input_ton
    if request_ton > sum_ton:
        additional_boilings = (request_ton - sum_ton) / 3 / input_ton
        if additional_boilings > 0:
            boilings_ricotta = Boilings()
            for order in orders:
                boilings_ricotta = proceed_order(order, df, boilings_ricotta)
                if order == orders[1]:
                    boiling_count_dict = {
                        "0.5": int(additional_boilings / 2),
                        "0.2": additional_boilings - int(additional_boilings / 2),
                    }
                    for key in boiling_count_dict.keys():
                        additional_df_05 = pd.DataFrame.from_dict(get_popular_sku(POPULAR_NAMES[key]))
                        boilings_ricotta = proceed_order(
                            order,
                            additional_df_05,
                            boilings_ricotta,
                            boiling_count_dict[key],
                        )

    boilings_ricotta.finish()
    return pd.DataFrame(boilings_ricotta.boilings), boilings_ricotta.boiling_number


def get_popular_sku(name):
    sku = db.session.query(RicottaSKU).filter(RicottaSKU.name == name).first()
    return {
        "sku": [sku],
        "plan": [sku.output_per_tank * 3],
        "boiling_id": [sku.made_from_boilings[0].id],
        "sku_id": [sku.id],
        "percent": [sku.made_from_boilings[0].percent],
        "flavoring_agent": [sku.made_from_boilings[0].flavoring_agent],
        "number_of_tanks": [sku.made_from_boilings[0].number_of_tanks],
        "short_display_name": [sku.made_from_boilings[0].short_display_name],
        "group": [sku.group.name],
        "is_cream": [sku.made_from_boilings[0].is_cream],
        "output_per_tank": [sku.output_per_tank],
        "at_first": False,
    }
