import os

os.environ["APP_ENVIRONMENT"] = "interactive"
from app.models import *

from app.scheduler.adygea.algo.boilings import *


def test_make_boiling():
    utils.lazy_tester.configure_function_path()
    boiling_model = cast_model(AdygeaBoiling, 1)
    utils.lazy_tester.log(make_boiling(boiling_model, 1))
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    utils.lazy_tester.verbose = True
    test_make_boiling()
