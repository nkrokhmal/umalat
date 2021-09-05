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

    boiling_plan_df = read_boiling_plan(boiling_plan_fn)

    if not schedule:
        schedule = make_schedule(
            boiling_plan_df,
            optimize=optimize,
            start_times=start_times,
            first_boiling_id=first_boiling_id,
        )
    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    res = submit_schedule(
        "моцарелла", schedule, frontend, prefix, STYLE, path=path, open_file=open_file
    )
    res["boiling_plan_df"] = boiling_plan_df
    return res

