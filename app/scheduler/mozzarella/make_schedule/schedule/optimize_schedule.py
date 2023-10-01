import collections

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.enum import LineName
from app.scheduler.mozzarella.make_schedule.schedule.calc_score import calc_score
from app.scheduler.mozzarella.make_schedule.schedule.make_boilings import make_boilings
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_from_boilings import make_schedule_from_boilings
from app.scheduler.mozzarella.make_schedule.schedule.optimize_schedule_by_swapping_water_gaps import (
    optimize_schedule_by_swapping_water_gaps,
)
from app.scheduler.mozzarella.make_schedule.schedule.parse_start_configuration import parse_start_configuration
from app.scheduler.time_utils import cast_t, cast_time


def _gen_seq(n, a=0, b=1):
    assert n != 0
    if n > 0:
        return [b] * n + [a]
    else:
        return [a] * abs(n) + [b]


def _parse_seq(seq, a=0, b=1):
    if seq[-1] == a:
        return len(seq) - 1
    else:
        return -(len(seq) - 1)


def test_seq():
    assert _gen_seq(-2) == [0, 0, 1]
    assert _gen_seq(2) == [1, 1, 0]
    assert _parse_seq([1, 1, 0]) == 2
    assert _parse_seq([0, 0, 1]) == -2

    try:
        _gen_seq(0)
    except AssertionError:
        pass


def optimize_schedule(
    boiling_plan_df,
    optimize_start_configurations=True,
    optimize_water_gaps=True,
    # - Make schedule basic kwargs
    optimize_cleanings=False,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    exact_start_time_line_name=None,
    start_configuration=None,
    date=None,
):
    # - Get start configuration if needed

    if not start_configuration:
        boilings_by_line_name = make_boilings(boiling_plan_df)
        schedule = make_schedule_from_boilings(
            boilings_by_line_name,
            cleanings={},
            start_times=start_times,
        )
        start_configuration = parse_start_configuration(schedule)  # maybe None if only one line

    # - Get neighbor start configurations

    if optimize_start_configurations and start_configuration:
        logger.debug("Initial start configuration", start_configuration=start_configuration)
        if not start_configuration:
            start_configurations = [None]
        else:
            start_configurations = []
            n = _parse_seq(start_configuration, a=LineName.WATER, b=LineName.SALT)
            with code("Calc neighborhood"):
                # - 1 -> -3, -2, -1, skip, 1,  2

                n_neighborhood = [n + i for i in range(-2, 3) if n + i != 0]

                # add one if skipped
                if 0 < n <= 2:
                    n_neighborhood.append(n - 2 - 1)
                if -2 <= n < 0:
                    n_neighborhood.append(n + 2 + 1)
                n_neighborhood = list(sorted(n_neighborhood))

            for _n in n_neighborhood:
                start_configurations.append(_gen_seq(_n, a=LineName.WATER, b=LineName.SALT))

        logger.debug("Start configurations", start_configurations=start_configurations)

        # - Filter invalid start configurations

        # count boiling per line
        counter = collections.Counter()
        for i, grp in boiling_plan_df.groupby("group_id"):
            counter[grp.iloc[0]["boiling"].line.name] += 1

        def _start_start_configuration_valid(sc):
            if not sc:
                return True
            for line_name in [LineName.WATER, LineName.SALT]:
                if sc.count(line_name) > counter[line_name]:
                    return False
            return True

        start_configurations = [
            configuration for configuration in start_configurations if _start_start_configuration_valid(configuration)
        ]
    else:
        start_configurations = [start_configuration]

    logger.debug("Optimizing start configurations", start_configuration=start_configurations)

    # - Make schedule with optimization for each start configuration

    res = []
    for configuration in start_configurations:
        if optimize_water_gaps:
            schedule = optimize_schedule_by_swapping_water_gaps(
                boiling_plan_df,
                # - Make schedule basic kwargs
                date=date,
                optimize_cleanings=optimize_cleanings,
                start_times=start_times,
                exact_start_time_line_name=exact_start_time_line_name,
                start_configuration=configuration,
            )
        else:
            schedule = make_schedule_basic(
                boiling_plan_df,
                date=date,
                optimize_cleanings=optimize_cleanings,
                start_times=start_times,
                exact_start_time_line_name=exact_start_time_line_name,
                start_configuration=configuration,
            )
        res.append(
            dict(
                schedule=schedule,
                date=date,
                optimize_cleanings=optimize_cleanings,
                start_times=start_times,
                exact_start_time_line_name=exact_start_time_line_name,
                start_configuration=configuration,
            )
        )
    logger.debug(
        "Optimization results",
        results=[
            calc_score(
                value["schedule"],
                start_times=start_times,
            )
            for value in res
        ],
    )

    # - Get output value

    value = min(
        res,
        key=lambda value: calc_score(
            value["schedule"],
            start_times=start_times,
        ),
    )  # return minimum score time
    schedule = value["schedule"]

    return schedule
