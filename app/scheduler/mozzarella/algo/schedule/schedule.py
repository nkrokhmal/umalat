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

    with code("Get start configuration"):
        with code("Make basic schedule"):
            boilings = make_boilings(boiling_plan_df, first_boiling_id=first_boiling_id)
            schedule = make_schedule_from_boilings(
                boilings, cleanings={}, start_times=start_times
            )

        with code("Get start configuration ob basic schedule"):
            boilings = list(
                sorted(
                    schedule["master"]["boiling", True],
                    key=lambda boiling: boiling.x[0],
                )
            )
            line_names = set(
                [boiling.props["boiling_model"].line.name for boiling in boilings]
            )

            if len(line_names) == 1:
                start_configuration = list(line_names)  # single element list
            else:
                start_configuration = []
                _cur_line_names = set()
                for boiling in boilings:
                    line_name = boiling.props["boiling_model"].line.name
                    _cur_line_names.add(line_name)
                    start_configuration.append(line_name)
                    if _cur_line_names == line_names:
                        break
        logger.debug(
            "Calculated start configuartion", start_configuration=start_configuration
        )

    # Fix start time of later line - make it as early as possible in greedy manner after the first line"
    if len(start_configuration) > 1:
        # at least two lines present
        start_times[start_configuration[-1]] = "00:00"

    with code("Find optimal cleanings"):
        if optimize:
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
        )
    return schedule
