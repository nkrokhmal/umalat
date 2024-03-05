import pandas as pd

from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def boiling_plan_create(df):
    if not df.empty:
        df["plan"] = df["plan"].apply(lambda x: round(x))
        df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
        df["group"] = df["sku"].apply(lambda x: x.group.name)
        df["boiling_type"] = df["sku"].apply(lambda x: x.made_from_boilings[0].name)

        result, boiling_number = handle_boiling(df)
        result["kg"] = result["plan"]
        result["name"] = result["sku"].apply(lambda sku: sku.name)
        result = result[
            [
                "id",
                "sku",
                "group",
                "name",
                "boiling_type",
                "kg",
            ]
        ]
        return result
    else:
        return pd.DataFrame(
            columns=[
                "id",
                "sku",
                "group",
                "name",
                "boiling_type",
                "kg",
            ]
        )


def proceed_order(order, df, boilings_brynza, boilings_count=1):
    df_filter = df[(df["group"] == "Брынза") | (df["group"] == "Чанах")]
    if not df_filter.empty:
        boilings_brynza.init_iterator(1e10)
        boilings_brynza.add_group(
            df_filter.to_dict("records"),
            boilings_count=boilings_count,
        )
    return boilings_brynza


def handle_boiling(df):
    boilings_brynza = Boilings()
    Order = collections.namedtuple("Collection", "group")
    orders = [
        Order("Брынза"),
    ]
    for order in orders:
        logger.info(df)
        boilings_brynza = proceed_order(order, df, boilings_brynza)

    boilings_brynza.finish()
    return pd.DataFrame(boilings_brynza.boilings), boilings_brynza.boiling_number
