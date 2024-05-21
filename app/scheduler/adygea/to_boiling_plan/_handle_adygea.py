import pandas as pd

from app.utils.features.merge_boiling_utils import Boilings


def _proceed_order(df_filter, boilings_adygea, boilings_count=1):
    if not df_filter.empty:
        boilings_adygea.init_iterator(df_filter["output"].iloc[0])
        boilings_adygea.add_group(
            df_filter.to_dict("records"),
            boilings_count=boilings_count,
        )
    return boilings_adygea


def _split_by_boilings(df: pd.DataFrame) -> pd.DataFrame:
    boilings_adygea = Boilings()
    for i, df_filter in df.groupby("group_id"):
        boilings_adygea = _proceed_order(df_filter, boilings_adygea)
    boilings_adygea.finish()
    return pd.DataFrame(boilings_adygea.boilings)
