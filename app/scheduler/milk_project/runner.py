import os

import openpyxl

from utils_ak.os.os_tools import makedirs

from app.globals import basedir
from app.scheduler.milk_project.algo.schedule import make_schedule
from app.scheduler.milk_project.boiling_plan.boiling_plan import read_boiling_plan
from app.scheduler.milk_project.frontend.frontend import wrap_frontend
from app.scheduler.milk_project.frontend.style import STYLE
from app.scheduler.submit_schedule import submit_schedule
from config import config


def run_milk_project(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    path="outputs/",
    prefix="",
    template_wb=None,
    first_batch_ids=None,
):
    makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn, first_batch_ids=first_batch_ids)
    start_time = start_time or "07:00"

    if not template_wb:
        template_wb = openpyxl.load_workbook(
            filename=os.path.join(basedir, config.TEMPLATE_SCHEDULE_PLAN_DEPARTMENT),
            data_only=True,
        )

    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    res = submit_schedule(
        "милкпроджект",
        schedule,
        frontend,
        prefix,
        STYLE,
        path=path,
        template_wb=template_wb,
        open_file=open_file,
    )
    res["boiling_plan_df"] = boiling_plan_df
    return res
