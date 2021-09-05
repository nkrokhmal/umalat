import pandas as pd

from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def boiling_plan_create(df, request_ton=0):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)
    df["number_of_tanks"] = 1

    result = handle_adygea(df)
    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["boiling_type"] = result["sku"].apply(
        lambda sku: sku.made_from_boilings[0].to_str()
    )
    result = result[
        [
            "id",
            "sku",
            "group",
            "output",
            "name",
            "boiling_type",
            "kg",
        ]
    ]
    return result


def handle_adygea(df):
    Order = collections.namedtuple("Collection", "group")
    orders = [
        Order("Рикотта"),
        Order("Кавказский"),
        Order("Черкесский"),
    ]
    adygea_dfs = []
    for i, order in enumerate(orders):
        df_grouped = df[df['group'] == order.group]
        df_grouped['id'] = i
        if not df.empty:
            adygea_dfs.append(df_grouped)
    return pd.concat(adygea_dfs)