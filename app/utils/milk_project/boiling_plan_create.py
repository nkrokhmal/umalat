from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)
    df["boiling_type"] = df["sku"].apply(lambda x: x.made_from_boilings[0].name)

    result, boiling_number = handle_milk_project(df)
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


def proceed_order(order, df, boilings_milk_project, boilings_count=1):
    df_filter = df[
        (df["group"] == order.group)
    ]
    if not df_filter.empty:
        boilings_milk_project.init_iterator(df_filter["output"].iloc[0])
        boilings_milk_project.add_group(
            df_filter.to_dict("records"),
            boilings_count=boilings_count,
        )
    return boilings_milk_project


def handle_milk_project(df):
    boilings_milk_project = Boilings()
    Order = collections.namedtuple("Collection", "group")
    orders = [
        Order("Рикотта"),
        Order("Четук"),
        Order("Качорикотта"),
    ]
    for order in orders:
        boilings_milk_project = proceed_order(order, df, boilings_milk_project)
    boilings_milk_project.finish()
    return pd.DataFrame(boilings_milk_project.boilings), boilings_milk_project.boiling_number

