from utils_ak.pandas.pandas_tools import mark_consecutive_groups


def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df.copy()
    df["sku_name"] = df["sku"].apply(lambda sku: sku.name)
    df["with_flavor"] = df["boiling"].apply(lambda boiling_model: boiling_model.with_flavor)

    mark_consecutive_groups(df, "boiling", "boiling_group_id")

    # mark number of tanks inside the boiling_group
    for boiling_group_id, grp in df.groupby("boiling_group_id"):
        df.loc[grp.index, "group_tanks"] = int(grp["tanks"].sum())

    return df
