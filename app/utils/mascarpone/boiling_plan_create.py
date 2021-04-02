import pandas as pd
from app import db
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings
from collections import namedtuple


def mascarpone_boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["flavoring_agent"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].flavoring_agent
    )
    df["group"] = df["sku"].apply(lambda x: x.group.name)

    result, boiling_number = handle_mascarpone(df)
    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["boiling_type"] = result["sku"].apply(
        lambda sku: sku.made_from_boilings[0].to_str()
    )
    result["output"] = result["max_boiling_weight"]
    max_output = int(result["output"].max())
    result["fermentators"] = result["output"].apply(lambda x: "1-2" if x == max_output else "3-4")
    result = result[
        [
            "id",
            "group",
            "output",
            "name",
            "boiling_type",
            "fermentators",
            "kg",
        ]
    ]
    return result


def proceed_order(order, df, boilings_mascarpone, output_tons):
    df_filter = df[
        (df["group"] == order.group)
        & (
            order.flavoring_agent is None
            or df["flavoring_agent"] == order.flavoring_agent
        )
    ]
    if not df_filter.empty:
        boilings_mascarpone.add_group(
            df_filter.to_dict("records"),
            max_weight=output_tons,
        )
    return boilings_mascarpone


def handle_mascarpone(df):
    boilings_mascarpone = Boilings()
    output_tons = sorted(list(set([x.output_ton for x in db.session.query(MascarponeFermentator).all()])), reverse=True)
    output_tons = [x + min(output_tons) for x in output_tons]

    Order = namedtuple("Collection", "flavoring_agent, group")
    orders = [
        Order("", "Маскарпоне"),
        Order("Шоколад-орех", "Маскарпоне"),
    ]
    for order in orders:
        boilings_ricotta = proceed_order(order, df, boilings_mascarpone, output_tons)
    boilings_ricotta.finish()
    return pd.DataFrame(boilings_ricotta.boilings), boilings_ricotta.boiling_number

