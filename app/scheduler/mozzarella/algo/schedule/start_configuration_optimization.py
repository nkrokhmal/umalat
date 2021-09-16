from app.imports.runtime import *
from .swap_optimization import optimize_schedule_by_swapping_water_gaps
from app.enum import LineName
from .score import calc_score


from .boilings import *
from .schedule_from_boilings import *
from .parse_start_configuration import *


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


def optimize_schedule_by_start_configuration(boiling_plan_df, *args, **kwargs):

    start_times = kwargs.get("start_times")
    start_configuration = kwargs.get("start_configuration")

    if not start_configuration:
        with code("Make basic schedule"):
            boilings = make_boilings(boiling_plan_df)
            schedule = make_schedule_from_boilings(
                boilings, cleanings={}, start_times=start_times
            )

        start_configuration = parse_start_configuration(schedule)

    logger.debug("Initial start configuration", start_configuration=start_configuration)
    if not start_configuration:
        start_configurations = [None]
    else:
        start_configurations = []
        n = _parse_seq(start_configuration, a=LineName.WATER, b=LineName.SALT)
        for i in range(-2, 2):
            _n = n + i
            if _n != 0:
                start_configurations.append(
                    _gen_seq(_n, a=LineName.WATER, b=LineName.SALT)
                )

    logger.debug("Start configurations", start_configurations=start_configurations)

    with code("Count boilings per line"):
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
