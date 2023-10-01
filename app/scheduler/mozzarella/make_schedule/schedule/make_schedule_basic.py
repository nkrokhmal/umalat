from typing import Literal, Optional

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.mozzarella.make_schedule.schedule.find_optimal_cleanings import find_optimal_cleanings
from app.scheduler.mozzarella.make_schedule.schedule.make_boilings import make_boilings
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_from_boilings import make_schedule_from_boilings
from app.scheduler.mozzarella.make_schedule.schedule.parse_start_configuration import parse_start_configuration
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan
from app.scheduler.time_utils import cast_t, cast_time, parse_time


def make_schedule_basic(
    boiling_plan_obj,
    optimize_cleanings=False,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    exact_start_time_line_name: Optional[str] = LineName.WATER,
    start_configuration=None,
    date=None,
):
    boiling_plan_df = to_boiling_plan(boiling_plan_obj)
    original_start_times = dict(start_times)
    start_times = dict(start_times)

    # - Get start configuration by approximate start_times

    if not start_configuration:
        # make basic schedule
        boilings = make_boilings(boiling_plan_df)
        schedule = make_schedule_from_boilings(boilings, cleanings={}, start_times=start_times)
        start_configuration = parse_start_configuration(schedule)

    # - Make tight schedule by approximate start_times

    # at least two lines present
    days, _, _ = parse_time(start_times[start_configuration[0]])

    # start latter before the former
    start_times[start_configuration[-1]] = cast_time(cast_t((days, 0, 0)))

    # - Find optimal cleanings

    if optimize_cleanings:
        cleanings = find_optimal_cleanings(
            boiling_plan_df=boiling_plan_df,
            start_times=start_times,
            start_configuration=start_configuration,
        )
        logger.debug("Found optimal cleanings", cleanings=cleanings)
    else:
        cleanings = boiling_plan_df.groupby("group_id").agg({"cleaning": "first"}).to_dict()["cleaning"]
        logger.debug("Using boiling plan cleanings", cleanings=cleanings)

    # - Make schedule with cleanings and start configuration

    cleanings = {k + boiling_plan_df["absolute_batch_id"].min() - 1: v for k, v in cleanings.items() if v}
    boilings = make_boilings(boiling_plan_df)
    schedule = make_schedule_from_boilings(
        boilings,
        cleanings=cleanings,
        start_times=start_times,
        start_configuration=start_configuration,
        date=date,
    )

    # - Fix start time for exact_start_time_line_name

    time_by_line = exact_start_time_line_name
    time_not_by_line = LineName.WATER if time_by_line == LineName.SALT else LineName.SALT

    boilings_by_line_name = {
        line_name: [
            boiling
            for boiling in schedule["master"]["boiling", True]
            if boiling.props["boiling_model"].line.name == line_name
        ]
        for line_name in [LineName.WATER, LineName.SALT]
    }

    if len(boilings_by_line_name.keys()) == 1:
        # Only one line - it is already fixed
        return schedule

    start_times[time_by_line] = original_start_times[time_by_line]
    start_times[time_not_by_line] = cast_time(
        cast_t(start_times[time_by_line])
        + boilings_by_line_name[time_not_by_line][0]["melting_and_packing"].x[0]
        - boilings_by_line_name[time_by_line][0]["melting_and_packing"].x[0]
    )

    # - If start_times changed - make final schedule

    if start_times != original_start_times:
        boilings = make_boilings(boiling_plan_df)
        schedule = make_schedule_from_boilings(
            boilings,
            cleanings=cleanings,
            start_times=start_times,
            start_configuration=start_configuration,
            date=date,
        )

    # - Return schedule

    return schedule


def test():
    make_schedule_basic(
        str(
            get_repo_path()
            / "app/data/static/samples/by_department/mozzarella/2023-09-22 План по варкам моцарелла.xlsx"
        ),
        start_times={LineName.WATER: "06:00", LineName.SALT: "11:00"},
    )


if __name__ == "__main__":
    test()
