import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.mascarpone.algo.schedule import *
from app.schedule_maker.departments.mascarpone.boiling_plan import *


def test():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = generate_random_boiling_plan()
    print(boiling_plan_df)
    print(make_schedule(boiling_plan_df))


if __name__ == "__main__":
    test()
