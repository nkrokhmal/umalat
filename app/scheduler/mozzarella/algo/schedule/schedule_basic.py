from app.scheduler.mozzarella.boiling_plan.boiling_plan import cast_boiling_plan

from app.scheduler.mozzarella.algo.schedule.find_optimal_cleanings.find_optimal_cleanings import *
from .parse_start_configuration import *


def make_schedule_basic(
    boiling_plan_obj,
    optimize_cleanings=False,
    start_times=None,
    start_configuration=None,
    date=None,
    next_boiling_optimization_type: Literal["chess", "lookahead"] = "lookahead",
):

    # - Cast boiling plan

    boiling_plan_df = cast_boiling_plan(boiling_plan_obj)

    # - Preprocess start times

    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    start_times = dict(start_times)

    # - Get start configuration

    if not start_configuration:

        # Make basic schedule
        boilings = make_boilings(boiling_plan_df)
        schedule = make_schedule_from_boilings(
            boilings,
            cleaning_type_by_group_id={},
            start_times=start_times,
            next_boiling_optimization_type=next_boiling_optimization_type,
        )

        start_configuration = parse_start_configuration(schedule)

    # - Preprocess start configuration

    if start_configuration:

        # at least two lines present
        days, _, _ = parse_time(start_times[start_configuration[0]])

        # start later before the former
        start_times[start_configuration[-1]] = cast_time(cast_t((days, 0, 0)))

    # - Find optimal cleanings

    if optimize_cleanings:
        cleaning_type_by_group_id = find_optimal_cleanings(
            boiling_plan_df,
            start_times,
            start_configuration=start_configuration,
            next_boiling_optimization_type=next_boiling_optimization_type,
        )
        logger.debug("Found optimal cleanings", cleanings=cleaning_type_by_group_id)
    else:
        cleaning_type_by_group_id = boiling_plan_df.groupby("group_id").agg({"cleaning": "first"}).to_dict()["cleaning"]
        logger.debug("Using boiling plan cleanings", cleanings=cleaning_type_by_group_id)

    # - Make schedule with cleanings and start configuration

    cleaning_type_by_group_id = {
        k + boiling_plan_df["absolute_batch_id"].min() - 1: v for k, v in cleaning_type_by_group_id.items() if v
    }
    boilings = make_boilings(boiling_plan_df)
    schedule = make_schedule_from_boilings(
        boilings,
        cleaning_type_by_group_id=cleaning_type_by_group_id,
        start_times=start_times,
        start_configuration=start_configuration,
        date=date,
        next_boiling_optimization_type=next_boiling_optimization_type,
    )

    # - Return

    return schedule
