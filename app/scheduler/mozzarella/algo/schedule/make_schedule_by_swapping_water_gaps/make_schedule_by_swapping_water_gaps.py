from app.imports.runtime import *  # isort: skip
from app.enum import LineName
from app.scheduler.mozzarella.algo.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.algo.schedule.make_schedule_by_swapping_water_gaps.combine_groups import combine_groups
from app.scheduler.mozzarella.algo.schedule.make_schedule_by_swapping_water_gaps.smart_shift import smart_shift
from app.scheduler.mozzarella.boiling_plan.parse_schedule import parse_schedule

from app.scheduler.mozzarella.algo.schedule.schedule_by_optimization import *
from app.scheduler.mozzarella.algo.schedule.calc_score import calc_score


def make_schedule_by_swapping_water_gaps(boiling_plan_df, **extra_make_schedule_basic_kwargs):

    # - Make basic schedule

    schedule = make_schedule_basic(boiling_plan_df, **extra_make_schedule_basic_kwargs)
    boiling_plan_df = parse_schedule(schedule)
    score = calc_score(schedule)

    water_boilings = [
        b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
    ]
    water_ids = [b.props["boiling_group_df"].iloc[0]["group_id"] for b in water_boilings]

    # - Go through all water boilings

    for water_id in water_ids[1:]:
        logger.debug("Optimizing", water_id=water_id)

        # - Calc current values

        current_boilings = schedule["master"]["boiling", True]
        current_ids = [b.props["boiling_group_df"].iloc[0]["group_id"] for b in current_boilings]
        current_water_boilings = [
            b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
        ]
        current_water_ids = [
            cur_water_boiling.props["boiling_group_df"].iloc[0]["group_id"]
            for cur_water_boiling in current_water_boilings
        ]

        # - Permutate boilings a little bit if possible

        previous_water_boiling, current_water_boiling = (
            current_water_boilings[current_water_ids.index(water_id) - 1],
            current_water_boilings[current_water_ids.index(water_id)],
        )
        previous_boiling = current_boilings[current_ids.index(water_id) - 1]

        if previous_boiling.props["boiling_model"].line.name == LineName.WATER:

            # swap only with salt boilings
            logger.debug("Previous boiling is WATER. Skipping swap optimization")
            continue

        if (
            current_water_boiling["melting_and_packing"]["collecting"].x[0]
            - previous_water_boiling["melting_and_packing"]["collecting"].y[0]
            <= 2
        ):
            logger.debug("Too small distance between water packings, skipping swap optimization")
            continue

        # - Prepare values for shifting

        values = [
            (b, b.props["boiling_group_df"].iloc[0]["group_id"], b.props["boiling_model"].line.name)
            for b in current_boilings
        ]
        logger.debug("Current values", values=[0 if v[2] == "Моцарелла в воде" else 1 for v in values])
        start_from = current_boilings.index(previous_boiling)
        values = smart_shift(values, start_from=start_from, key=lambda v: 0 if v[2] == "Моцарелла в воде" else 1)
        logger.debug("Shifted values", values=[0 if v[2] == "Моцарелла в воде" else 1 for v in values])

        swapped_df = combine_groups(boiling_plan_df, [v[1] for v in values])

        # - Calc new schedule

        swapped_schedule = make_schedule_basic(swapped_df)
        swapped_score = calc_score(swapped_schedule)
        logger.debug("Got new score", score=score, swapped_score=swapped_score)

        # - Check if new schedule is better

        if swapped_score < score:

            # success - found something better!
            logger.debug("Optimization successful", score=score, swapped_score=swapped_score)
            boiling_plan_df = swapped_df
            schedule = swapped_schedule
            score = swapped_score

    # - Return

    return schedule
