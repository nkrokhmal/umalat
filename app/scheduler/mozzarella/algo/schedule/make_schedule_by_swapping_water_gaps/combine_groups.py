import pandas as pd


def combine_groups(boiling_plan_df, groups):
    dfs = []
    for g in groups:
        dfs.append(boiling_plan_df[boiling_plan_df["group_id"] == g])
    df = pd.concat(dfs)
    df = df.reset_index(drop=True)
    return df
