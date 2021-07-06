import os

os.environ["environment"] = "interactive"

from app.imports.runtime import *
from app.scheduler.contour_cleanings.algo.schedule import *


def test():
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    fns = {
        "mozzarella": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/2021-02-09 Моцарелла Расписание.pickle",
        "mascarpone": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/2021-04-21 Маскарпоне Расписание.pickle",
        "butter": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/Sample Маслоцех Расписание.pickle",
        "milk_project": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/Sample Милк-проджект Расписание.pickle",
        "ricotta": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/2021-05-15 Рикотта Расписание.pickle",
    }
    schedules = {}
    for key, fn in fns.items():
        with open(fn, "rb") as f:
            schedules[key] = ParallelepipedBlock.from_dict(pickle.load(f))

    utils.lazy_tester.log(make_contour_1(schedules))
    utils.lazy_tester.log(make_contour_2(schedules))
    utils.lazy_tester.log(make_contour_3(schedules))
    utils.lazy_tester.log(make_contour_4(schedules))
    utils.lazy_tester.log(make_contour_5(schedules))
    utils.lazy_tester.log(make_contour_6(schedules))
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    test()
