import os

os.environ["environment"] = "interactive"

import warnings

warnings.filterwarnings("ignore")

from app.interactive_imports import *


def test():
    makedirs("schedules/")
    # fn = os.path.join(basedir, "app/data/inputs/2021-02-08 План по варкам.xlsx")
    # fn = os.path.join(basedir, "app/data/inputs/2021-02-17 План по варкам.xlsx")
    fn = os.path.join(basedir, "app/data/inputs/2021-04-13 План по варкам.xlsx")
    fn = os.path.join(basedir, "app/data/inputs/2021-04-13 Расписание.xlsx")
    boiling_plan_df = read_boiling_plan(fn)
    start_times = {LineName.WATER: "02:00", LineName.SALT: "10:00"}
    boilings = make_boilings(boiling_plan_df)
    schedule = make_schedule(boilings, start_times=start_times)

    try:
        frontend = make_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    draw_excel_frontend(frontend, open_file=True, fn="schedules/schedule.xlsx")


if __name__ == "__main__":
    test()
