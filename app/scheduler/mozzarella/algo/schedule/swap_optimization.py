from app.imports.runtime import *

from app.enum import LineName
from app.scheduler.mozzarella.boiling_plan.parser import parse_schedule

from .schedule_basic import make_schedule_basic
from .schedule_by_optimization import *


def calc_score(schedule):
    line_lengths = {}
    for line_name in [LineName.WATER, LineName.SALT]:
        boilings = [
            b
            for b in schedule["master"]["boiling", True]
            if b.props["boiling_model"].line.name == line_name
        ]
        beg = min(b.x[0] for b in boilings)
        end = max(b.y[0] for b in boilings)
        line_lengths[line_name] = end - beg
    score = line_lengths[LineName.WATER] + line_lengths[LineName.SALT] / 3
    return score


def swap_groups(df, group_id1, group_id2):
    df = df.reset_index(drop=True)

    indexes1 = df[df["group_id"] == group_id1].index
    indexes2 = df[df["group_id"] == group_id2].index
    indexes1, indexes2 = map(list, [indexes1, indexes2])
    indexes1, indexes2 = list(
        sorted([indexes1, indexes2], key=lambda indexes: indexes[0])
    )

    indexes = []
    indexes += [i for i in df.index if i < indexes1[0]]
    indexes += indexes2
    indexes += [i for i in df.index if indexes1[-1] < i < indexes2[0]]
    indexes += indexes1
    indexes += [i for i in df.index if i > indexes2[-1]]

    return df.iloc[indexes].reset_index(drop=True)


def optimize_schedule_by_swapping_water_gaps(boiling_plan_df, *args, **kwargs):
    with code("Make initial schedule"):
        schedule = make_schedule_basic(boiling_plan_df, *args, **kwargs)
        score = calc_score(schedule)

        water_boilings = [
            b
            for b in schedule["master"]["boiling", True]
            if b.props["boiling_model"].line.name == LineName.WATER
        ]
        water_ids = [
            b.props["boiling_group_df"].iloc[0]["group_id"] for b in water_boilings
        ]

    for water_id in water_ids[1:]:
        logger.debug("Optimizing", water_id=water_id)
        cur_boilings = schedule["master"]["boiling", True]
        cur_ids = [
            b.props["boiling_group_df"].iloc[0]["group_id"] for b in cur_boilings
        ]
        cur_water_boilings = [
            b
            for b in schedule["master"]["boiling", True]
            if b.props["boiling_model"].line.name == LineName.WATER
        ]
        cur_water_ids = [
            b.props["boiling_group_df"].iloc[0]["group_id"] for b in cur_water_boilings
        ]

        bw_prev, bw_cur = (
            cur_water_boilings[cur_water_ids.index(water_id) - 1],
            cur_water_boilings[cur_water_ids.index(water_id)],
        )
        b_prev = cur_boilings[cur_ids.index(water_id) - 1]

        if b_prev.props["boiling_model"].line.name == LineName.WATER:
            # swap only with salt boilings
            continue

        bs_prev = b_prev

        swapped_df = swap_groups(
            boiling_plan_df,
            bs_prev.props["boiling_group_df"].iloc[0]["group_id"],
            bw_cur.props["boiling_group_df"].iloc[0]["group_id"],
        )
        swapped_schedule = make_schedule_basic(swapped_df, *args, **kwargs)
        swapped_score = calc_score(swapped_schedule)

        if swapped_score < score:
            # success - found something betteer!
            logger.debug(
                "Optimization successful", score=score, swapped_score=swapped_score
            )
            boiling_plan_df = swapped_df
            schedule = swapped_schedule
            score = swapped_score
    return schedule
