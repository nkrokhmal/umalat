from app.imports.runtime import *
from app.scheduler.contour_cleanings import *
from app.scheduler.frontend import *


def run_contour_cleanings(
    path,
    prefix="",
):
    utils.makedirs(path)

    fns = {}
    for a, b in [['mozzarella', 'Расписание моцарелла',
                  'mascarpone', 'Расписание маскарпоне',
                  'butter', 'Расписание маслоцех',
                  'milk_project', 'Расписание милкпроджект',
                  'ricotta', 'Расписание рикотта']]:
        fns[a] = os.path.join(path, )

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

    return {"schedule": schedule, "frontend": frontend}
