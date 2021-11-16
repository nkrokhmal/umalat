from app.enum import LineName
from app.scheduler.mozzarella.boiling_plan.boiling_plan import cast_boiling_plan

from .schedule_from_boilings import *
from .schedule_by_optimization import *
from .parse_start_configuration import *


def make_schedule_basic(
    boiling_plan_obj,
    optimize_cleanings=False,
    start_times=None,
    start_configuration=None,
    first_boiling_id=1,
    date=None,
):
    boiling_plan_df = cast_boiling_plan(boiling_plan_obj)
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    start_times = dict(start_times)

    with code("Get start configuration"):
        if not start_configuration:
            with code("Make basic schedule"):
                boilings = make_boilings(
                    boiling_plan_df, first_boiling_id=first_boiling_id
                )
                schedule = make_schedule_from_boilings(
                    boilings, cleanings={}, start_times=start_times
                )

            start_configuration = parse_start_configuration(schedule)

    if start_configuration:
        # at least two lines present
        start_times[start_configuration[-1]] = "00:00"

    with code("Find optimal cleanings"):
        if optimize_cleanings:
            cleanings = find_optimal_cleanings(
                boiling_plan_df, start_times, start_configuration=start_configuration
            )
            logger.debug("Found optimal cleanings", cleanings=cleanings)
        else:
            cleanings = (
                boiling_plan_df.groupby("group_id")
                .agg({"cleaning": "first"})
                .to_dict()["cleaning"]
            )
            logger.debug("Using boiling plan cleanings", cleanings=cleanings)

    with code("Make schedule with cleanings and start configuration "):
        cleanings = {k + first_boiling_id - 1: v for k, v in cleanings.items() if v}
        boilings = make_boilings(boiling_plan_df, first_boiling_id=first_boiling_id)
        schedule = make_schedule_from_boilings(
            boilings,
            cleanings=cleanings,
            start_times=start_times,
            start_configuration=start_configuration,
            date=date,
        )
    return schedule
