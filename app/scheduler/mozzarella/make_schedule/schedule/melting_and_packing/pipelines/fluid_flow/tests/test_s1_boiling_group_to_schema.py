import os
import warnings

from utils_ak.pandas.pandas_tools import mark_consecutive_groups

from config import config


os.environ["APP_ENVIRONMENT"] = "test"


warnings.filterwarnings("ignore")


def test(use_interactive_environment):
    df = read_boiling_plan(config.abs_path("app/data/static/samples/mozzarella/2021-02-09 План по варкам.xlsx"))
    mark_consecutive_groups(df, "boiling", "boiling_group")
    boiling_group_df = df[df["boiling_group"] == 2]
    boiling_volumes, boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
    print(boiling_volumes, boilings_meltings, packings)


if __name__ == "__main__":
    test(True)
