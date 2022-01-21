from app.scheduler.mascarpone.algo.cleanings import *


def test():
    utils.lazy_tester.configure_function_path()
    utils.lazy_tester.log(make_cleaning("separator"))
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    test()
