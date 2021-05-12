from app.enum import LineName
from app.schedule_maker.departments.mozarella import *
from app.schedule_maker.departments.mozarella.boiling_plan.boiling_plan import (
    read_boiling_plan,
)

from .schedule_from_boilings import *
from .schedule_by_optimization import *


def make_schedule(fn, optimize=False, start_times=None, first_group_id=1):
    boiling_plan_df = read_boiling_plan(fn)

    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}

    if optimize:
        schedule = make_schedule_with_boiling_inside_a_day(
            boiling_plan_df, start_times=start_times, first_group_id=first_group_id
        )
    else:
        cleanings = (
            boiling_plan_df.groupby("group_id")
            .agg({"cleaning": "first"})
            .to_dict()["cleaning"]
        )
        cleanings = {k: v for k, v in cleanings.items() if v}
        boilings = make_boilings(boiling_plan_df, first_group_id=first_group_id)
        schedule = make_schedule_from_boilings(
            boilings, cleanings=cleanings, start_times=start_times
        )
    return schedule
