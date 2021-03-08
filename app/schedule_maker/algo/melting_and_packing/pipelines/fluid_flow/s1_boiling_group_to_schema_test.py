import os

os.environ["environment"] = "interactive"

from app.schedule_maker import mark_consecutive_groups
from app.schedule_maker.algo import *
from config import DebugConfig

import warnings

warnings.filterwarnings("ignore")


def test():
    df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/sample_boiling_plan.xlsx")
    )
    mark_consecutive_groups(df, "boiling", "boiling_group")
    boiling_group_df = df[df["boiling_group"] == 2]
    transformer = BoilingGroupToSchema()
    boiling_volumes, boilings_meltings, packings = transformer(boiling_group_df)
    print(boiling_volumes, boilings_meltings, packings)


if __name__ == "__main__":
    test()
