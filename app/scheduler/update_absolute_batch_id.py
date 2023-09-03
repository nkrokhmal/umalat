import pandas as pd


def update_absolute_batch_id(boiling_plan_df: pd.DataFrame, first_batch_ids_by_type: dict):
    # - Set absolute_batch_id

    boiling_plan_df["absolute_batch_id"] = boiling_plan_df["batch_id"]

    # - Add first_batch_id to absolute_batch_id

    for batch_type, grp in boiling_plan_df.groupby("batch_type"):
        boiling_plan_df.loc[grp.index, "absolute_batch_id"] += (
            first_batch_ids_by_type.get(batch_type, 1) - grp["batch_id"].min()
        )

    # - Return

    return boiling_plan_df
