from app.imports.runtime import *
from app.scheduler.mascarpone import *
from app.scheduler.frontend import *
from app.scheduler.submit import submit


def run_mascarpone(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    start_batch_id=1,
    path="outputs/",
    prefix="",
):
    utils.makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    start_time = start_time or "07:00"

    if not schedule:
        schedule = make_schedule(
            boiling_plan_df, start_time=start_time, start_batch_id=start_batch_id
        )

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    return submit(schedule, frontend, path, prefix, STYLE, open_file=open_file)
