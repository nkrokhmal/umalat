import os

os.environ["APP_ENVIRONMENT"] = "interactive"
from app.models import *

from app.scheduler.ricotta.algo.boilings import *
from app.scheduler.ricotta.boiling_plan import *


def test_make_boiling():
    utils.lazy_tester.configure_function_path()
    boiling_model = cast_model(RicottaBoiling, 17)
    utils.lazy_tester.log(make_boiling(boiling_model))
    utils.lazy_tester.assert_logs()


def test_make_boiling_sequence():
    # todo: make random seed and use lazy tester for output
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 0]
    print(make_boiling_sequence(boiling_group_df))


# todo: archived
# def test_make_boiling_group():
#     # todo: make random seed and use lazy tester for output
#     boiling_plan_df = generate_random_boiling_plan()
#     boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 0]
#     print(make_boiling_group(boiling_group_df))


if __name__ == "__main__":
    test_make_boiling()
    test_make_boiling_sequence()
    # test_make_boiling_group()
