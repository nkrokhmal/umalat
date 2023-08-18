import os

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester


os.environ["APP_ENVIRONMENT"] = "interactive"


def test_boiling():
    lazy_tester.configure_function_path()
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 2]
    lazy_tester.log(make_boiling(boiling_group_df))
    lazy_tester.assert_logs()


def test_boiling_sequence():
    lazy_tester.configure_function_path()
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 2]
    boilings = [make_boiling(boiling_group_df) for _ in range(3)]
    lazy_tester.log(make_boiling_sequence(boilings))
    lazy_tester.assert_logs()


if __name__ == "__main__":
    test_boiling()
    test_boiling_sequence()
