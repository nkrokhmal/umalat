import os

os.environ["environment"] = "interactive"

from app.schedule_maker.ricotta.boiling_plan import *
from config import DebugConfig


def test_read_boiling_plan():
    df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/ricotta/sample_boiling_plan.xlsx")
    )
    print(df[["boiling_id", "sku_name", "kg", "tanks"]].head())
    print(df.iloc[0])


if __name__ == "__main__":
    test_read_boiling_plan()
