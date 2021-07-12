from app.imports.runtime import *
from app.scheduler.mozzarella import *
from app.scheduler.submit import submit_schedule


def run_mozzarella(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_times=None,
    first_boiling_id=1,
    optimize=True,
    path="outputs/",
    prefix="",
):
    start_times = start_times or {LineName.WATER: "02:00", LineName.SALT: "06:00"}

    if not schedule:
        schedule = make_schedule(
            boiling_plan_fn,
            optimize=optimize,
            start_times=start_times,
            first_boiling_id=first_boiling_id,
        )

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    return submit_schedule(
        "моцарелла", schedule, frontend, path, prefix, STYLE, open_file=open_file
    )
