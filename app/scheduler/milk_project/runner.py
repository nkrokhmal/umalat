from app.imports.runtime import *
from app.scheduler.milk_project import *
from app.scheduler.frontend import *
from app.scheduler.submit import submit_schedule


def run_milk_project(
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
    return submit_schedule('милкпроджект', schedule, frontend, path, prefix, STYLE, open_file=open_file)
