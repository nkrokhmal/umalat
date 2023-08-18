from utils_ak.os.os_tools import makedirs

from app.scheduler.adygea.algo.schedule import make_schedule
from app.scheduler.mascarpone.boiling_plan.boiling_plan import read_boiling_plan
from app.scheduler.mascarpone.frontend.frontend import wrap_frontend
from app.scheduler.submit import submit_schedule


def run_mascarpone(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    first_mascarpone_batch_id=1,
    first_cream_batch_id=10,
    first_robiola_batch_id=100,
    first_cream_cheese_batch_id=1000,
    first_cottage_cheese_batch_id=10000,
    path="outputs/",
    prefix="",
):
    makedirs(path)
    boiling_plan_df = read_boiling_plan(
        boiling_plan_fn,
        first_batch_ids={
            "mascarpone": first_mascarpone_batch_id,
            "cream": first_cream_batch_id,
            "robiola": first_robiola_batch_id,
            "cream_cheese": first_cream_cheese_batch_id,
            "cottage_cheese": first_cottage_cheese_batch_id,
        },
    )
    start_time = start_time or "07:00"

    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    res = submit_schedule("маскарпоне", schedule, frontend, prefix, STYLE, path=path, open_file=open_file)
    res["boiling_plan_df"] = boiling_plan_df
    return res
