from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def boiling_plan_create(df, request_ton=0):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)
    df["number_of_tanks"] = 1

    result, boiling_number = handle_adygea(df)
    result["kg"] = result["plan"]
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["boiling_type"] = result["sku"].apply(
        lambda sku: sku.made_from_boilings[0].to_str()
    )
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
    result['kg'] = result.apply(lambda x: x['output'] if x['boiling_count'] > 1 else x['kg'], axis=1)
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
    df["number_of_tanks"] = df["boiling_count"].apply(lambda x: math.floor(x))

    return df.groupby("name", as_index=False).agg(agg)


def proceed_order(order, df, boilings_adygea, boilings_count=1):
    df_filter = df[df["group"] == order.group]
    if not df_filter.empty:
        df_filter_groups = [group for _, group in df_filter.groupby(["sku_id"])]
        for df_filter_group in df_filter_groups:
            boilings_adygea.init_iterator(df_filter_group["output"].iloc[0])
            boilings_adygea.add_group(
                df_filter_group.to_dict("records"),
                boilings_count=boilings_count,
            )
    return boilings_adygea


def handle_adygea(df):
    boilings_adygea = Boilings()
    Order = collections.namedtuple("Collection", "group")
    orders = [
        Order("Рикотта"),
        Order("Кавказский"),
        Order("Черкесский"),
    ]
    for order in orders:
        boilings_adygea = proceed_order(order, df, boilings_adygea)
    boilings_adygea.finish()
    return pd.DataFrame(boilings_adygea.boilings), boilings_adygea.boiling_number
