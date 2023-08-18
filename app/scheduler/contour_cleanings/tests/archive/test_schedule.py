import os

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester

from app.scheduler.load_properties import load_properties
from app.scheduler.load_schedules import load_schedules


os.environ["APP_ENVIRONMENT"] = "interactive"


def test():
    configure_loguru_stdout("INFO")
    lazy_tester.configure_function_path()
    schedules = load_schedules(
        "/Users/marklidenberg/Yandex.Disk.localized/Загрузки/umalat/2021-07-17/approved",
        "2021-07-17",
    )

    properties = load_properties(schedules)

    lazy_tester.log(make_contour_1(schedules, properties))
    lazy_tester.log(make_contour_2(schedules, properties))
    lazy_tester.log(make_contour_3(schedules, properties))
    lazy_tester.log(make_contour_4(schedules, properties))
    lazy_tester.log(make_contour_5(schedules, properties))
    lazy_tester.log(make_contour_6(schedules, properties))
    lazy_tester.assert_logs(reset=False)


if __name__ == "__main__":
    test()
