import os


os.environ["APP_ENVIRONMENT"] = "interactive"


def test_make_boiling():
    lazy_tester.configure_function_path()
    boiling_model = cast_model(RicottaBoiling, 17)
    lazy_tester.log(make_boiling(boiling_model))
    lazy_tester.assert_logs()


def test_make_boiling_sequence():
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 0]
    print(make_boiling_sequence(boiling_group_df))


if __name__ == "__main__":
    test_make_boiling()
    test_make_boiling_sequence()
    # test_make_boiling_group()
