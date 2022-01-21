import os

os.environ["APP_ENVIRONMENT"] = "interactive"

from app.scheduler.ricotta.algo.cleanings import *


def test():
    utils.lazy_tester.configure_function_path()
    utils.lazy_tester.log(make_bath_cleanings())
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    test()
