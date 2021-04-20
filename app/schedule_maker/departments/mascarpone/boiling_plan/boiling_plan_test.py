import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.mascarpone.boiling_plan import *
from config import DebugConfig


def test_read_boiling_plan():
    print(
        read_boiling_plan(
            DebugConfig.abs_path(
                "app/data/inputs/mascarpone/2021_04_21_План_по_варкам_маскарпоне_14.xlsx"
            )
        )[["batch_id", "boiling_id", "sku", "kg"]]
    )


if __name__ == "__main__":
    test_read_boiling_plan()
