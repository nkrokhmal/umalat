from app.scheduler.butter.boiling_plan import *


def test_random():
    utils.lazy_tester.configure_function_path()
    utils.lazy_tester.log(generate_random_boiling_plan())
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    test_random()
