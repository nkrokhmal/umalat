from app.imports.runtime import *
from app.enum import LineName
from app.scheduler.mozzarella.algo.schedule.make_schedule import make_schedule
from app.scheduler.mozzarella.boiling_plan import read_boiling_plan
from app.scheduler.mozzarella.frontend.wrap_frontend import wrap_frontend
from app.scheduler.mozzarella.frontend.style import STYLE

from app.scheduler.submit import submit_schedule
from utils_ak.clock import clock
from typing import Optional, Literal


def run_mozzarella(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_times=None,
    first_batch_id=1,
    optimization_strategy: Optional[Literal["swap", "lookahead"]] = 'swap',
    path="outputs/",
    prefix="",
):
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}

    boiling_plan_df = read_boiling_plan(boiling_plan_fn, first_batch_ids={"mozzarella": first_batch_id})
    if not schedule:
        schedule = make_schedule(
            boiling_plan_df,
            optimization_strategy=optimization_strategy,
            make_schedule_basic_kwargs=dict(start_times=start_times),
        )
    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    res = submit_schedule("моцарелла", schedule, frontend, prefix, STYLE, path=path, open_file=open_file)
    res["boiling_plan_df"] = boiling_plan_df
    return res


pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)


def test():
    clock.enable()
    clock("start")
    utils.configure_loguru(level="DEBUG")

    run_mozzarella(
        "/Users/arsenijkadaner/Desktop/2023-06-13 Расписание моцарелла.xlsx",
        start_times={LineName.WATER: "06:00", LineName.SALT: "06:00"},
        first_batch_id=1,
        open_file=True,
        prefix="test",
        optimization_strategy='lookahead'
    )

    clock("start")
    print(clock.stats())


if __name__ == "__main__":
    test()
