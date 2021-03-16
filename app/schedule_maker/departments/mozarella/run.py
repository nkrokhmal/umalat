from app.schedule_maker.departments.mozarella import *
from app.schedule_maker.departments.mozarella.algo.schedule.boilings import (
    make_boilings,
)  # todo: hardcode, for some reaosn not found
from app.enum import *
from app.schedule_maker.frontend import *


def run(fn, optimize=False, open_file=True, **kwargs):
    boiling_plan_df = read_boiling_plan(fn)
    cleanings = (
        boiling_plan_df.groupby("group_id")
        .agg({"cleaning": "first"})
        .to_dict()["cleaning"]
    )
    cleanings = {k: v for k, v in cleanings.items() if v}
    start_times = {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    boilings = make_boilings(boiling_plan_df, first_group_id=1)

    if optimize:
        schedule = make_schedule_with_boiling_inside_a_day(
            boiling_plan_df, start_times=start_times, first_group_id=1
        )
    else:
        schedule = make_schedule(boilings, cleanings=cleanings, start_times=start_times)
    frontend = make_frontend(schedule, coolings_mode="all")
    schedule_wb = draw_excel_frontend(
        frontend, MOZARELLA_STYLE, open_file=open_file, fn="schedules/schedule.xlsx"
    )


if __name__ == "__main__":
    main()
