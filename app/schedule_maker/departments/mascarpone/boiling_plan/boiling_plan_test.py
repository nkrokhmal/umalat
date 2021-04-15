import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.mascarpone.boiling_plan import *
from config import DebugConfig


def test_read_boiling_plan():
    print(
        read_boiling_plan(
            DebugConfig.abs_path(
                "app/data/inputs/mascarpone/2021.04.06 План по варкам.xlsx"
            )
        )
    )


if __name__ == "__main__":
    test_read_boiling_plan()