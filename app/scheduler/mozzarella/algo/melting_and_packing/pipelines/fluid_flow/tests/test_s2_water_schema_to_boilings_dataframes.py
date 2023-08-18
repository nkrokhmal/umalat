import os


os.environ["APP_ENVIRONMENT"] = "interactive"

import warnings


warnings.filterwarnings("ignore")


def test():
    df = read_boiling_plan(os.path.join(basedir, "app/schedule_maker/data/sample_boiling_plan.xlsx"))
    mark_consecutive_groups(df, "boiling", "boiling_group")
    boiling_group_df = df[df["boiling_group"] == 2]
    print(boiling_group_df)
    boiling_model = boiling_group_df.iloc[0]["boiling"]
    boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataframes()(
        boilings_meltings, packings, boiling_model.line.melting_speed, round=False
    )
    for boiling_dataframes in boilings_dataframes:
        print(boiling_dataframes["meltings"])
        print(boiling_dataframes["coolings"])
        for packing_team_id, df in boiling_dataframes["packings"].items():
            print(df)
        print()


if __name__ == "__main__":
    test2()
