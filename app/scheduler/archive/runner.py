import os
import pickle

from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.os.os_tools import makedirs
from utils_ak.split_file.split_file import SplitFile

from app.scheduler.frontend import draw_excel_frontend
from app.scheduler.submit import submit_schedule


def submit_schedule(name, schedule, frontend, path, prefix, style, open_file=False):
    makedirs(path)
    with code("Dump schedule as pickle file"):
        base_fn = f"Расписание {name}.pickle"
        if prefix:
            base_fn = prefix + " " + base_fn
        output_pickle_fn = os.path.join(path, base_fn)
        output_pickle_fn = SplitFile(output_pickle_fn).get_new()

        with open(output_pickle_fn, "wb") as f:
            pickle.dump(schedule.to_dict(), f)

    with code("Dump frontend as excel file"):
        base_fn = f"Расписание {name}.xlsx"
        if prefix:
            base_fn = prefix + " " + base_fn
        output_fn = os.path.join(path, base_fn)

        draw_excel_frontend(frontend, open_file=open_file, fn=output_fn, style=style)

    return {"schedule": schedule, "frontend": frontend}


def run_schedule(
    module,
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    path="outputs/",
    prefix="",
):
    makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    start_time = start_time or "07:00"

    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    return submit_schedule("масло", schedule, frontend, path, prefix, STYLE, open_file=open_file)
