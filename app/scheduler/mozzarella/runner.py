from app.enum import LineName
from app.scheduler.mozzarella.algo.schedule.schedule import make_schedule
from app.scheduler.mozzarella.boiling_plan.boiling_plan import read_boiling_plan
from app.scheduler.mozzarella.frontend.frontend import wrap_frontend
from app.scheduler.submit import submit_schedule


def run_mozzarella(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_times=None,
    first_batch_id=1,
    optimize=True,
    optimize_cleanings=True,
    path="outputs/",
    prefix="",
):
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}

    boiling_plan_df = read_boiling_plan(boiling_plan_fn, first_batch_ids={"mozzarella": first_batch_id})
    if not schedule:
        schedule = make_schedule(
            boiling_plan_df,
            optimize=optimize,
            optimize_cleanings=optimize_cleanings,
            start_times=start_times,
        )
    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    res = submit_schedule("моцарелла", schedule, frontend, prefix, STYLE, path=path, open_file=open_file)
    res["boiling_plan_df"] = boiling_plan_df
    return res
