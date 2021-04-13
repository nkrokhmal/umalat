from utils_ak.pandas import *


def saturate_boiling_plan(boiling_plan_df):
    boiling_plan_df["boiling"] = boiling_plan_df["sku"].apply(
        lambda sku: sku.made_from_boilings[0]
    )
    return boiling_plan_df
