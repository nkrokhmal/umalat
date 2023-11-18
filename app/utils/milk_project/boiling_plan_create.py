import pandas as pd


def boiling_plan_create(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        df["kg"] = df["plan"].apply(lambda x: round(x))
        df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
        df["group"] = df["sku"].apply(lambda x: x.group.name)
        df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)
        df["boiling_type"] = df["sku"].apply(lambda x: x.made_from_boilings[0].name)
        df["kg"] = df["plan"]
        df["name"] = df["sku"].apply(lambda sku: sku.name)
        return df[["id", "sku", "group", "name", "boiling_type", "kg"]]
    else:
        return pd.DataFrame(
            columns=[
                "id",
                "sku",
                "group",
                "name",
                "boiling_type",
                "kg",
            ]
        )
