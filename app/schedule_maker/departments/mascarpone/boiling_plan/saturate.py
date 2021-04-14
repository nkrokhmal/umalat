from utils_ak.pandas import *


def saturate_boiling_plan(boiling_plan_df):
    boiling_plan_df["boiling"] = boiling_plan_df["sku"].apply(
        lambda sku: sku.made_from_boilings[0]
    )
    # todo: make properly
    boiling_plan_df["is_cream"] = boiling_plan_df["sku"].apply(
        lambda sku: "сливки" in sku.name.lower()
    )
    return boiling_plan_df
