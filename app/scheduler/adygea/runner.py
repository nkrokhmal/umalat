from app.imports.runtime import *
from app.scheduler.adygea import *
from app.scheduler.submit import submit_schedule
from app.scheduler.boiling_plan import *

def run_adygea(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    prepare_start_time=None,
    first_batch_id=1,
    path="outputs/",
    prefix="",
    template_wb=None,
):
    start_time = start_time or "07:00"
    prepare_start_time = prepare_start_time or start_time
    utils.makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn, first_batch_ids={'adygea': first_batch_id})

    if not schedule:
        schedule = make_schedule(
            boiling_plan_df, start_time=start_time, prepare_start_time=prepare_start_time
        )
    if not template_wb:
        template_wb = openpyxl.load_workbook(
            filename=os.path.join(basedir, config.TEMPLATE_SCHEDULE_PLAN_DEPARTMENT),
            data_only=True,
        )
    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    res = submit_schedule(
        "адыгейский",
        schedule,
        frontend,
        prefix,
        STYLE,
        path=path,
        open_file=open_file,
        template_wb=template_wb,
    )
    res["boiling_plan_df"] = boiling_plan_df
    return res
