from app.scheduler.mozzarella.algo.schedule.schedule_basic import make_schedule_basic

from .make_boilings import *
from .parse_start_configuration import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_schedule_from_boilings import *
from .score import calc_score
from .swap_optimization import optimize_schedule_by_swapping_water_gaps


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


def optimize_schedule_by_start_configuration(
    boiling_plan_df,
    exact_melting_time_by_line=None,
    *args,
    **kwargs,
):

    # - Preprocess arguments

    start_times = kwargs.get("start_times")
    start_configuration = kwargs.get("start_configuration")

    # - Get start configuration from schedule

    if not start_configuration:

        # - Make basic schedule

        line_name_to_line_boilings = make_boilings(boiling_plan_df)
        schedule = make_schedule_from_boilings(
            line_name_to_line_boilings,
            cleaning_type_by_group_id={},
            start_times=start_times,
            next_boiling_optimization_type="chess",
        )

        # - Get start configuration

        start_configuration = parse_start_configuration(schedule)

    # _- Get start configurations
    logger.debug("Initial start configuration", start_configuration=start_configuration)

    if not start_configuration:
        start_configurations = [None]
    else:
        start_configurations = []

        # - Get n (todo: better naming, doc)

        n = _parse_seq(start_configuration, a=LineName.WATER, b=LineName.SALT)

        # - Calc neighborhood

        # [- 1 -> -3, -2, -1, skip, 1,  2]

        n_neighborhood = [n + i for i in range(-2, 3) if n + i != 0]

        # add one if skipped
        if 0 < n <= 2:
            n_neighborhood.append(n - 2 - 1)
        if -2 <= n < 0:
            n_neighborhood.append(n + 2 + 1)
        n_neighborhood = list(sorted(n_neighborhood))

        # - Generate start configurations

        for _n in n_neighborhood:
            start_configurations.append(_gen_seq(_n, a=LineName.WATER, b=LineName.SALT))

    logger.debug("Start configurations", start_configurations=start_configurations)

    # - Count boilings per line

    counter = collections.Counter()
    for i, grp in boiling_plan_df.groupby("group_id"):
        counter[grp.iloc[0]["boiling"].line.name] += 1

    # - Filter valid start configurations

    def _start_start_configuration_valid(sc):
        if not sc:
            return True
        for line_name in [LineName.WATER, LineName.SALT]:
            if sc.count(line_name) > counter[line_name]:
                return False
        return True

    start_configurations = [
        start_configuration
        for start_configuration in start_configurations
        if _start_start_configuration_valid(start_configuration)
    ]

    logger.debug("Optimizing start configurations", start_configuration=start_configurations)

    # - Run optimization

    values = []
    for start_configuration in start_configurations:
        schedule = optimize_schedule_by_swapping_water_gaps(
            boiling_plan_df,
            start_configuration=start_configuration,
            next_boiling_optimization_type="chess",
            *args,
            **kwargs,
        )
        values.append(
            {
                "schedule": schedule,
                "start_configuration": start_configuration,
                "args": args,
                "kwargs": kwargs,
            }
        )

    # - Get output value

    best_value = min(
        values, key=lambda value: calc_score(value["schedule"], start_times=start_times)
    )  # return minimum score time

    logger.debug(
        "Optimization results",
        best_result={
            "score": calc_score(best_value["schedule"], start_times=start_times),
            "start_configuration": best_value["start_configuration"],
        },
        results=[
            {
                "score": calc_score(value["schedule"], start_times=start_times),
                "start_configuration": value["start_configuration"],
            }
            for value in values
        ],
    )

    # - Fix start time if needed

    if exact_melting_time_by_line:
        start_times = dict(start_times)

        time_by_line = exact_melting_time_by_line
        time_not_by_line = LineName.WATER if time_by_line == LineName.SALT else LineName.SALT

        boilings = best_value["schedule"]["master"]["boiling", True]

        line_name_to_line_boilings = {
            line_name: [boiling for boiling in boilings if boiling.props["boiling_model"].line.name == line_name]
            for line_name in [LineName.WATER, LineName.SALT]
        }

        if not all(line_name_to_line_boilings.values()):
            return best_value["schedule"]

        first_line_boilings_by_line_name = {k: v[0] for k, v in line_name_to_line_boilings.items()}
        first_boiling = min(first_line_boilings_by_line_name.values(), key=lambda boiling: boiling.x[0])
        second_boiling = max(first_line_boilings_by_line_name.values(), key=lambda boiling: boiling.x[0])
        if first_boiling.props["boiling_model"].line.name == time_by_line:
            # time already set by proper line

            return best_value["schedule"]
        else:
            start_times[time_not_by_line] = cast_time(
                cast_t(start_times[time_not_by_line])
                + cast_t(start_times[time_by_line])
                - second_boiling["melting_and_packing"].x[0]
            )

            return optimize_schedule_by_swapping_water_gaps(
                boiling_plan_df,
                start_configuration=[boiling.props["boiling_model"].line.name for boiling in boilings], # fix order from optimization
                next_boiling_optimization_type="chess",
                *args,
                **kwargs,
            )
    else:
        return best_value["schedule"]
