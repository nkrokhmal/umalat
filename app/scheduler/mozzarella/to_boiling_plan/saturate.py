def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df.copy()
    df["line"] = df["boiling"].apply(lambda boiling_model: boiling_model.line)
    df["boiling_volumes"] = df["line"].apply(lambda line: [line.output_kg])
    df["sku_name"] = df["sku"].apply(lambda sku: sku.name)
    return df
