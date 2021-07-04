from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)
    df["boiling_type"] = df["sku"].apply(lambda x: x.made_from_boilings[0].name)

    result, boiling_number = handle_milkproject(df)
    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result = result[
        [
            "id",
            "sku",
            "group",
            # "output",
            "name",
            "boiling_type",
            "kg",
        ]
    ]
    return result


def proceed_order(order, df, boilings_milkproject, boilings_count=1):
    df_filter = df[
        (df["group"] == order.group)
    ]
    if not df_filter.empty:
        boilings_milkproject.init_iterator(df_filter["output"].iloc[0])
        boilings_milkproject.add_group(
            df_filter.to_dict("records"),
            boilings_count=boilings_count,
        )
    return boilings_milkproject


def handle_milkproject(df):
    boilings_milkproject = Boilings()
    Order = collections.namedtuple("Collection", "group")
    orders = [
        Order("Рикотта"),
        Order("Четук"),
        Order("Качорикотта"),
    ]
    for order in orders:
        boilings_milkproject = proceed_order(order, df, boilings_milkproject)
    boilings_milkproject.finish()
    return pd.DataFrame(boilings_milkproject.boilings), boilings_milkproject.boiling_number

