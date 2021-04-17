from utils_ak.pandas import *


def saturate_boiling_plan(boiling_plan_df):
    boiling_plan_df["boiling"] = boiling_plan_df["sku"].apply(
        lambda sku: sku.made_from_boilings[0]
    )
    # todo: make properly
    boiling_plan_df["is_cream"] = boiling_plan_df["sku"].apply(
        lambda sku: "сливки" in sku.name.lower()
    )
    boiling_plan_df["sourdough_range"] = boiling_plan_df["sourdough_range"].astype(str)
    boiling_plan_df["sourdoughs"] = boiling_plan_df["sourdough_range"].apply(
        lambda s: s.split("-")
    )
    return boiling_plan_df
