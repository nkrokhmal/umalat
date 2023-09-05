import pandas as pd

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.enum import LineName
from app.scheduler.mozzarella.make_schedule.schedule.calc_score import calc_score
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.to_boiling_plan.parse_schedule_basic_info import parse_schedule_basic_info


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


# todo later: del, deprecated [@marklidenberg]
# def swap_groups(df, group_id1, group_id2):
#     logger.debug("Swapping groups", gid1=group_id1, gid2=group_id2)
#     df = df.reset_index(drop=True)
#
#     indexes1 = df[df["group_id"] == group_id1].index
#     indexes2 = df[df["group_id"] == group_id2].index
#     indexes1, indexes2 = map(list, [indexes1, indexes2])
#     indexes1, indexes2 = list(
#         sorted([indexes1, indexes2], key=lambda indexes: indexes[0])
#     )
#
#     indexes = []
#     indexes += [i for i in df.index if i < indexes1[0]]
#     indexes += indexes2
#     indexes += [i for i in df.index if indexes1[-1] < i < indexes2[0]]
#     indexes += indexes1
#     indexes += [i for i in df.index if i > indexes2[-1]]
#
#     return df.iloc[indexes].reset_index(drop=True)


def optimize_schedule_by_swapping_water_gaps(boiling_plan_df, *args, **kwargs):
    with code("Make initial schedule"):
        schedule = make_schedule_basic(boiling_plan_df, *args, **kwargs)
        boiling_plan_df = parse_schedule_basic_info(schedule)
        score = calc_score(schedule)

        water_boilings = [
            b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
        ]
        water_ids = [b.props["boiling_group_df"].iloc[0]["group_id"] for b in water_boilings]

    for water_id in water_ids[1:]:
        logger.debug("Optimizing", water_id=water_id)

        with code("Calc cur values"):
            cur_boilings = schedule["master"]["boiling", True]
            cur_ids = [b.props["boiling_group_df"].iloc[0]["group_id"] for b in cur_boilings]
            cur_water_boilings = [
                b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
            ]
            cur_water_ids = [b.props["boiling_group_df"].iloc[0]["group_id"] for b in cur_water_boilings]

        with code("Permutate boilings a little bit if possible"):
            bw_prev, bw_cur = (
                cur_water_boilings[cur_water_ids.index(water_id) - 1],
                cur_water_boilings[cur_water_ids.index(water_id)],
            )
            b_prev = cur_boilings[cur_ids.index(water_id) - 1]

            if b_prev.props["boiling_model"].line.name == LineName.WATER:
                # swap only with salt boilings
                logger.debug("Previous boiling is WATER. Skipping swap optimization")
                continue

            if (
                bw_cur["melting_and_packing"]["collecting"].x[0] - bw_prev["melting_and_packing"]["collecting"].y[0]
                <= 2
            ):
                logger.debug("Too small distance between water packings, skipping swap optimization")
                continue

            with code("Prepare values for shifting"):
                values = [
                    (b, b.props["boiling_group_df"].iloc[0]["group_id"], b.props["boiling_model"].line.name)
                    for b in cur_boilings
                ]
                logger.debug("Current values", values=[0 if v[2] == "Моцарелла в воде" else 1 for v in values])
                start_from = cur_boilings.index(b_prev)
                values = smart_shift(
                    values, start_from=start_from, key=lambda v: 0 if v[2] == "Моцарелла в воде" else 1
                )
                logger.debug("Shifted values", values=[0 if v[2] == "Моцарелла в воде" else 1 for v in values])

            swapped_df = combine_groups(boiling_plan_df, [v[1] for v in values])

        swapped_schedule = make_schedule_basic(swapped_df, *args, **kwargs)
        swapped_score = calc_score(swapped_schedule)
        logger.debug("Got new score", score=score, swapped_score=swapped_score)
        if swapped_score < score:
            # success - found something better!
            logger.debug("Optimization successful", score=score, swapped_score=swapped_score)
            boiling_plan_df = swapped_df
            schedule = swapped_schedule
            score = swapped_score
    return schedule
