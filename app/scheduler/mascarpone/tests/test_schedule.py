from app.scheduler.mascarpone.algo.schedule import *
from app.scheduler.mascarpone.boiling_plan import *
from config import DebugConfig


def test():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path(
            "app/data/inputs/mascarpone/2021.04.06 План по варкам.xlsx"
        )
    )
    print(make_schedule(boiling_plan_df))


if __name__ == "__main__":
    test()
