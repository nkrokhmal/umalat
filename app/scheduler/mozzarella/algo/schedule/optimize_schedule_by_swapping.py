from app.scheduler.mozzarella.algo.schedule.schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.boiling_plan.parser import parse_schedule

from app.scheduler.mozzarella.algo.schedule.find_optimal_cleanings.find_optimal_cleanings import *
from .calc_score import calc_score


def smart_shift(s, key=None, start_from=0):
    if start_from > 0:
        return s[:start_from] + smart_shift(s[start_from:], key=key)

    # swap first zero with one. If next element is not zero - repeat for following elements
    key = key or (lambda v: v)

    assert all([key(v) in [0, 1] for v in s])

    if len(s) <= 1:
        return s

    if key(s[0]) == 0:

        # first zero
        return s

    if all(key(v) == 1 for v in s):

        # all ones
        return s

    with code("Find last one before zero: 1, 1, 1, 0 -> 2"):
        last_one_index = -1
        for i in range(len(s)):
            if key(s[i]) == 1:
                last_one_index += 1
            else:
                break

    return (
        s[:last_one_index] + [s[last_one_index + 1], s[last_one_index]] + smart_shift(s[last_one_index + 2 :], key=key)
    )


def test_smart_shift():
    assert smart_shift([1, 1, 0, 1, 1, 0, 1, 0, 1, 0]) == [1, 0, 1, 1, 0, 1, 0, 1, 0, 1]


def combine_groups(boiling_plan_df, groups):
    dfs = []
    for g in groups:
        dfs.append(boiling_plan_df[boiling_plan_df["group_id"] == g])
    df = pd.concat(dfs)
    df = df.reset_index(drop=True)
    return df


def optimize_schedule_by_swapping(
    boiling_plan_df,
    *args,
    **kwargs,
):

    # - Make initial schedule

    schedule = make_schedule_basic(boiling_plan_df, *args, **kwargs)
    boiling_plan_df = parse_schedule(schedule)
    score = calc_score(schedule)

    boilings = schedule["master"]["boiling", True]

    # - Find the best schedule

    for boiling_id, line_name in [
        [boiling.props["boiling_id"], boiling.props["boiling_model"].line.name] for boiling in boilings
    ]:
        logger.debug("Optimizing", boiling_id=boiling_id)

        # - Calc current values

        current_boilings = schedule["master"]["boiling", True]
        current_ids = [boiling.props["boiling_group_df"].iloc[0]["group_id"] for boiling in current_boilings]
        current_line_boilings = [
            boiling
            for boiling in schedule["master"]["boiling", True]
            if boiling.props["boiling_model"].line.name == line_name
        ]
        current_line_ids = [boiling.props["boiling_group_df"].iloc[0]["group_id"] for boiling in current_line_boilings]

        # - Permutate boilings a little bit if possible

        prev_line_boiling, current_line_boiling = (
            current_line_boilings[current_line_ids.index(boiling_id) - 1],
            current_line_boilings[current_line_ids.index(boiling_id)],
        )
        prev_boiling = current_boilings[current_ids.index(boiling_id) - 1]

        if prev_boiling.props["boiling_model"].line.name == line_name:
            # swap only with dirrent line

            logger.debug("Previous boiling is the same line. Skipping swap optimization")
            continue

        if (
            current_line_boiling["melting_and_packing"]["collecting", True][0].x[0]
            - prev_line_boiling["melting_and_packing"]["collecting", True][-1].y[0]
            <= 1000
        ):
            logger.debug("Too small distance between packings, skipping swap optimization")
            continue

        # Prepare values for shifting
        values = [
            (boiling, boiling.props["boiling_group_df"].iloc[0]["group_id"], boiling.props["boiling_model"].line.name)
            for boiling in current_boilings
        ]

        logger.trace("Current values", values=[0 if v[2] == line_name else 1 for v in values])

        start_from = current_boilings.index(prev_boiling)
        values = smart_shift(values, start_from=start_from, key=lambda v: 0 if v[2] == line_name else 1)

        logger.trace("Shifted values", values=[0 if v[2] == line_name else 1 for v in values])

        swapped_df = combine_groups(boiling_plan_df, [v[1] for v in values])

        # - Calc new schedule

        swapped_schedule = make_schedule_basic(swapped_df, *args, **kwargs)
        new_score = calc_score(swapped_schedule)

        logger.debug("Got new score", score=score, new_score=new_score, is_better=new_score < score)

        if new_score < score:
            # success - found something better!

            logger.trace("Optimization successful", score=score, swapped_score=new_score)
            boiling_plan_df = swapped_df
            schedule = swapped_schedule
            score = new_score

    return schedule
