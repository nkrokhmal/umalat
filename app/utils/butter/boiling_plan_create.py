from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def butter_boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["weight"] = df["sku"].apply(lambda x: round(x.weight_netto))
    df["flavoring_agent"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].flavoring_agent
        if isinstance(x, ButterSKU)
        else ""
    )
    df["is_lactose"] = df["sku"].apply(lambda x: x.made_from_boilings[0].is_lactose)
    df["group"] = df["sku"].apply(lambda x: x.group.name)
    df["name"] = df["sku"].apply(lambda x: x.name)
    df["output"] = df["sku"].apply(lambda x: x.line.output_kg)
    return handle_butter(df)


def butter_proceed_order(order, df, boilings):
    df_filter = df[
        (df["is_lactose"] == order.is_lactose)
        & (
            order.flavoring_agent is None
            or df["flavoring_agent"] == order.flavoring_agent
        )
    ]
    if not df_filter.empty:
        df_filter_groups = [group for _, group in df_filter.groupby("percent")]

        for df_filter_group in df_filter_groups:
            df_group_dict = df_filter_group.sort_values(
                by="weight",
                ascending=True,
            ).to_dict("records")

            boilings.add_group(
                df_group_dict,
            )
    return boilings


def handle_butter(df):
    output_kg = db.session.query(ButterLine).all()[0].output_kg
    boilings_butter = Boilings(max_weight=output_kg, min_weight=output_kg)
    Order = collections.namedtuple("Collection", "flavoring_agent, is_lactose")
    orders = [
        Order("", True),
        Order("", False),
        Order("Соль", True),
        Order("Соль", False),
    ]
    for order in orders:
        boilings_butter = butter_proceed_order(
            order, df, boilings_butter,
        )
    boilings_butter.finish()
    return pd.DataFrame(boilings_butter.boilings)
