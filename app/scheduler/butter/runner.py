from app.imports.runtime import *
from app.scheduler.butter.algo import make_schedule
from app.scheduler.butter.boiling_plan import read_boiling_plan
from app.scheduler.butter.frontend import wrap_frontend, STYLE
from app.scheduler.frontend import *
from app.scheduler.submit import submit_schedule


def run_butter(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    path="outputs/",
    prefix="",
):
    utils.makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    start_time = start_time or "07:00"

    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    res = submit_schedule(
        "масло",
        schedule,
        frontend,
        prefix,
        STYLE,
        path=path,
        open_file=open_file,
    )
    res["boiling_plan_df"] = boiling_plan_df
    return res
