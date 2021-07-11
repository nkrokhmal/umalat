from app.imports.runtime import *
from app.scheduler.contour_cleanings import *
from app.scheduler.frontend import *
from app.scheduler.submit import submit_schedule


def run_contour_cleanings(
    path,
    schedule=None,
    prefix="",
    open_file=False,
):
    utils.makedirs(path)

    schedules = {}
    for a, b in [
        ["mozzarella", "Расписание моцарелла"],
        ["mascarpone", "Расписание маскарпоне"],
        ["butter", "Расписание масло"],
        ["milk_project", "Расписание милкпроджект"],
        ["ricotta", "Расписание рикотта"],
    ]:
        fn = os.path.join(path, prefix + " " + b + ".pickle")
        with open(fn, "rb") as f:
            schedules[a] = ParallelepipedBlock.from_dict(pickle.load(f))
    if not schedule:
        schedule = make_schedule(schedules)
    frontend = wrap_frontend(schedule)
    return submit_schedule(
        "контурные мойки", schedule, frontend, path, prefix, STYLE, open_file=open_file
    )
