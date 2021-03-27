import pandas as pd
from app import db
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings
from collections import namedtuple


def boiling_plan_create(df, request_ton=0):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["flavoring_agent"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].flavoring_agent
    )
    df["number_of_tanks"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].number_of_tanks
    )
    df["short_display_name"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].short_display_name
    )
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["is_cream"] = df["sku"].apply(lambda x: x.made_from_boilings[0].is_cream)
    df["output_per_tank"] = df["sku"].apply(lambda x: x.output_per_tank)

    result, boiling_number = handle_ricotta(df, request_ton=request_ton)
    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["output"] = result["output_per_tank"] * result["number_of_tanks"]
    result["boiling_type"] = result["sku"].apply(
        lambda sku: sku.made_from_boilings[0].to_str()
    )
    result = result[
        ["id", "number_of_tanks", "group", "output", "name", "boiling_type", "kg"]
    ]
    return result


def proceed_order(order, df, boilings_ricotta):
    df_filter = df[
        (df["is_cream"] == order.is_cream)
        & (
                order.flavoring_agent is None
                or df["flavoring_agent"] == order.flavoring_agent
        )
        ]
    if not df_filter.empty:
        df_filter["output"] = (
                df_filter["number_of_tanks"] * df_filter["output_per_tank"]
        )
        df_filter["output"] = df_filter["output"].apply(lambda x: int(x))
        df_filter_groups = [group for _, group in df_filter.groupby("output")]
        for df_filter_group in df_filter_groups:
            max_weight = df_filter_group["output"].iloc[0]
            boilings_ricotta.add_group(
                df_filter_group.to_dict("records"), max_weight=max_weight
            )
    return boilings_ricotta


def handle_ricotta(df, request_ton=0):
    boilings_ricotta = Boilings()
    input_ton = db.session.query(RicottaLine).first().input_ton
    Order = namedtuple("Collection", "is_cream, flavoring_agent")
    orders = [
        Order(True, None),
        Order(False, ""),
        Order(False, "Ваниль"),
        Order(False, "Шоколад"),
        Order(False, "Шоколад-орех"),
    ]
    for order in orders:
        boilings_ricotta = proceed_order(order, df, boilings_ricotta)
    boilings_ricotta.finish()
    sum_ton = pd.DataFrame(boilings_ricotta.boilings).groupby('id').first()['number_of_tanks'].sum() * input_ton
    if request_ton > sum_ton:
        additional_boilings = (request_ton - sum_ton) / 3 / input_ton
        if additional_boilings > 0:
            boilings_ricotta = Boilings()
            for order in orders:
                boilings_ricotta = proceed_order(order, df, boilings_ricotta)
                if order == orders[1]:
                    additional_df = pd.DataFrame.from_dict(get_popular_sku(additional_boilings))
                    boilings_ricotta = proceed_order(order, additional_df, boilings_ricotta)
    boilings_ricotta.finish()
    return pd.DataFrame(boilings_ricotta.boilings), boilings_ricotta.boiling_number


def get_popular_sku(count):
    sku = db.session.query(RicottaSKU).filter(RicottaSKU.name == 'Рикотта "Pretto", 45%, 0,2 кг, пл/с').first()
    return {
        'sku': [sku],
        'plan': [sku.output_per_tank * 3 * count],
        'boiling_id': [sku.made_from_boilings[0].id],
        'sku_id': [sku.id],
        'percent': [sku.made_from_boilings[0].percent],
        'flavoring_agent': [sku.made_from_boilings[0].flavoring_agent],
        'number_of_tanks': [sku.made_from_boilings[0].number_of_tanks],
        'short_display_name': [sku.made_from_boilings[0].short_display_name],
        'group': [sku.group.name],
        'is_cream': [sku.made_from_boilings[0].is_cream],
        'output_per_tank': [sku.output_per_tank],
    }
