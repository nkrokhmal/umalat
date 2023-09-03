import pandas as pd

from app.models import AdygeaSKU, cast_model
from app.utils.features.merge_boiling_utils import Boilings


def _proceed_order(df_filter, boilings_adygea, boilings_count=1):
    if not df_filter.empty:
        boilings_adygea.init_iterator(df_filter["output"].iloc[0])
        boilings_adygea.add_group(
            df_filter.to_dict("records"),
            boilings_count=boilings_count,
        )
    return boilings_adygea


def _handle_adygea(df):
    df["sku"] = df["sku"].apply(lambda sku: cast_model(AdygeaSKU, sku))
    df["plan"] = df["kg"]
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)

    boilings_adygea = Boilings()
    for i, df_filter in df.groupby("group_id"):
        boilings_adygea = _proceed_order(df_filter, boilings_adygea)
    boilings_adygea.finish()
    return pd.DataFrame(boilings_adygea.boilings), boilings_adygea.boiling_number
