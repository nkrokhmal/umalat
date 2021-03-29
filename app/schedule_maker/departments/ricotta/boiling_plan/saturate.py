def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df.copy()
    df["sku_name"] = df["sku"].apply(lambda sku: sku.name)
    df["with_flavor"] = df["boiling"].apply(
        lambda boiling_model: boiling_model.with_flavor
    )
    return df
