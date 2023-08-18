import os


os.environ["APP_ENVIRONMENT"] = "interactive"

from app.imports.runtime import *
from app.scheduler import load_properties, load_schedules
from app.scheduler.contour_cleanings.algo.schedule import *


def test():
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()
    schedules = load_schedules(
        "/Users/marklidenberg/Yandex.Disk.localized/Загрузки/umalat/2021-07-17/approved",
        "2021-07-17",
    )

    properties = load_properties(schedules)

    utils.lazy_tester.log(make_contour_1(schedules, properties))
    utils.lazy_tester.log(make_contour_2(schedules, properties))
    utils.lazy_tester.log(make_contour_3(schedules, properties))
    utils.lazy_tester.log(make_contour_4(schedules, properties))
    utils.lazy_tester.log(make_contour_5(schedules, properties))
    utils.lazy_tester.log(make_contour_6(schedules, properties))
    utils.lazy_tester.assert_logs(reset=False)


if __name__ == "__main__":
    test()
