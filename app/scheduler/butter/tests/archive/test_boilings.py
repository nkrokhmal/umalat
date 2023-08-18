import os


os.environ["APP_ENVIRONMENT"] = "interactive"
from app.models import *
from app.scheduler.butter.algo.boilings import *
from app.scheduler.butter.boiling_plan import *


def test_boiling():
    utils.lazy_tester.configure_function_path()
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 0]
    utils.lazy_tester.log(make_boiling(boiling_group_df))
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    test_boiling()
