from utils_ak.pandas import *


def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df
    df["boiling"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0])

    df["sourdough_range"] = df["sourdough_range"].astype(str)
    df["sourdoughs"] = df["sourdough_range"].apply(lambda s: s.split("-"))
    df["sourdoughs"] = df["sourdoughs"].apply(
        lambda lst: [str(int(float(s))) for s in lst]
    )

    df["sku_cls_name"] = df["sku"].apply(lambda sku: str(sku.__class__))

    def get_type(cls_name):
        if "Mascarpone" in cls_name:
            return "mascarpone"
        elif "CreamCheese" in cls_name:
            return "cream_cheese"

    df["type"] = df["sku_cls_name"].apply(get_type)
    df["is_cream"] = df["sku"].apply(lambda sku: "сливки" in sku.name.lower())

    return boiling_plan_df
