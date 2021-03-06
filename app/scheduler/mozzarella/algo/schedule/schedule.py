from app.enum import LineName
from app.scheduler.mozzarella import *
from app.scheduler.mozzarella.boiling_plan.boiling_plan import (
    cast_boiling_plan,
)

from .schedule_from_boilings import *
from .schedule_by_optimization import *


def make_schedule(
    boiling_plan_obj, optimize=False, start_times=None, first_boiling_id=1
):
    boiling_plan_df = cast_boiling_plan(boiling_plan_obj)
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    if optimize:
        cleanings = find_optimal_cleanings(boiling_plan_df, start_times)
    else:
        cleanings = (
            boiling_plan_df.groupby("group_id")
            .agg({"cleaning": "first"})
            .to_dict()["cleaning"]
        )

    cleanings = {k + first_boiling_id - 1: v for k, v in cleanings.items() if v}
    boilings = make_boilings(boiling_plan_df, first_boiling_id=first_boiling_id)
    schedule = make_schedule_from_boilings(
        boilings, cleanings=cleanings, start_times=start_times
    )
    return schedule
