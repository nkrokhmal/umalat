from app.imports.runtime import *
from .swap_optimization import optimize_schedule_by_swapping_water_gaps
from app.enum import LineName
from .score import calc_score


def optimize_schedule_by_start_configuration(boiling_plan_df, *args, **kwargs):
    start_configurations = [
        [LineName.WATER],
        [LineName.SALT],
        [LineName.WATER, LineName.SALT],
        [LineName.WATER, LineName.WATER, LineName.SALT],
        [LineName.SALT, LineName.WATER],
        [LineName.SALT, LineName.SALT, LineName.WATER],
    ]

    with code("Count boilings per line"):
        counter = collections.Counter()
        for i, grp in boiling_plan_df.groupby("group_id"):
            counter[grp.iloc[0]["boiling"].line.name] += 1

    def _start_start_configuration_valid(sc):
        for line_name in [LineName.WATER, LineName.SALT]:
            if sc.count(line_name) > counter[line_name]:
                return False
        return True

    start_configurations = [
        sc for sc in start_configurations if _start_start_configuration_valid(sc)
    ]

    logger.debug(
        "Optimizing start configurations", start_configuration=start_configurations
    )

    with code("Optimization"):
        res = []
        for sc in start_configurations:
            schedule = optimize_schedule_by_swapping_water_gaps(
                boiling_plan_df, start_configuration=sc, *args, **kwargs
            )
            res.append(schedule)
    logger.debug(
        "Optimization results", results=[calc_score(schedule) for schedule in res]
    )
    return min(res, key=calc_score)  # return minimum score time
