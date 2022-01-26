from app.imports.runtime import *
from app.scheduler.ricotta import *
from app.scheduler.submit import submit_schedule


def run_ricotta(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    first_boiling_id=1,
    path="outputs/",
    prefix="",
):
    utils.makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    start_time = start_time or "07:00"
    if not schedule:
        schedule = make_schedule(
            boiling_plan_df, start_time=start_time, first_boiling_id=first_boiling_id
        )

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    res = submit_schedule(
        "рикотта", schedule, frontend, prefix, STYLE, path=path, open_file=open_file
    )
    res["boiling_plan_df"] = boiling_plan_df
    return res
