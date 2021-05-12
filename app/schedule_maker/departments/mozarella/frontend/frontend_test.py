import os

os.environ["environment"] = "interactive"

import warnings

warnings.filterwarnings("ignore")

from config import basedir
from app.schedule_maker.departments.mozarella import *


def test():
    makedirs("schedules/")
    # fn = os.path.join(basedir, "app/data/inputs/2021-02-08 План по варкам.xlsx")
    # fn = os.path.join(basedir, "app/data/inputs/2021-02-17 План по варкам.xlsx")
    # fn = os.path.join(basedir, "app/data/inputs/2021-04-13 План по варкам.xlsx")
    fn = os.path.join(basedir, "app/data/inputs/2021-05-07 План по варкам.xlsx")
    boiling_plan_df = read_boiling_plan(fn)
    start_times = {LineName.WATER: "02:00", LineName.SALT: "06:00"}
    boilings = make_boilings(boiling_plan_df, first_group_id=74)
    schedule = make_schedule(boilings, start_times=start_times)
    # schedule = make_schedule_with_boiling_inside_a_day(
    #     boiling_plan_df, start_times=start_times, first_group_id=74
    # )

    try:
        frontend = make_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    draw_excel_frontend(
        frontend, open_file=True, fn="schedules/schedule.xlsx", style=STYLE
    )


if __name__ == "__main__":
    test()
