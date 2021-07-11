from app.imports.runtime import *
from app.scheduler import draw_excel_frontend
from app.scheduler.contour_cleanings.algo.schedule import *
from app.scheduler.contour_cleanings.frontend import *


def test(open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    from utils_ak.loguru import configure_loguru_stdout

    fns = {
        "mozzarella": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание моцарелла.pickle",
        "mascarpone": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание маскарпоне.pickle",
        "butter": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание масло.pickle",
        "milk_project": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание милкпроджект.pickle",
        "ricotta": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание рикотта.pickle",
    }
    schedules = {}
    for key, fn in fns.items():
        with open(fn, "rb") as f:
            schedules[key] = ParallelepipedBlock.from_dict(pickle.load(f))

    schedule = make_schedule(schedules)

    frontend = wrap_frontend(schedule)

    utils.lazy_tester.log(frontend)
    draw_excel_frontend(frontend, STYLE, open_file=open_file)

    utils.lazy_tester.assert_logs(reset=True)

    # todo soon: make properly
    with open(
        "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Контурные мойки.pickle",
        "wb",
    ) as f:
        pickle.dump(schedule.to_dict(), f)


if __name__ == "__main__":
    test(open_file=False)
