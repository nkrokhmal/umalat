import numpy as np


def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df.copy()
    df["line"] = df["boiling"].apply(lambda boiling_model: boiling_model.line)

    # set default configuration if missing
    df["configuration"] = np.where(
        df["configuration"] == "missing",
        df["line"].apply(lambda line: str(line.input_ton)),
        df["configuration"],
    )

    # fill boiling volumes
    values = []
    for i, row in df.iterrows():
        values.append(
            [float(x.strip()) * row["line"].output_kg / row["line"].input_ton for x in row["configuration"].split(",")]
        )
    df["boiling_volumes"] = values

    df["sku_name"] = df["sku"].apply(lambda sku: sku.name)

    return df
