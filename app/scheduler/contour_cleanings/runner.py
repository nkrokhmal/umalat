from app.imports.runtime import *
from app.scheduler.contour_cleanings import *
from app.scheduler.frontend import *
from app.scheduler.submit import submit_schedule
from app.scheduler.load_schedules import *


def run_contour_cleanings(
    input_path,
    output_path="outputs/",
    schedule=None,
    prefix="",
    open_file=False,
    **kwargs,
):
    schedules = load_schedules(input_path, prefix=prefix)
    assert_schedules_presence(
        schedules,
        raise_if_not_present=["mozzarella", "ricotta"],
        warn_if_not_present=["butter", "adygea", "milk_project", "mascarpone"],
    )

    for department in ["butter", "milk_project", "adygea"]:
        if kwargs.get(f"{department}_end_time"):
            schedules[department] = "manual"

    if not schedule:
        schedule = make_schedule(schedules, **kwargs)
    frontend = wrap_frontend(schedule)
    return submit_schedule(
        "контурные мойки",
        schedule,
        frontend,
        output_path,
        prefix,
        STYLE,
        open_file=open_file,
    )
