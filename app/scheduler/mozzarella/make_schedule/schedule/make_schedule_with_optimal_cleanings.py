from typing import Literal, Optional

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.mozzarella.make_schedule.schedule.find_optimal_cleanings import (
    _find_optimal_cleanings_combination_by_schedule,
)
from app.scheduler.mozzarella.make_schedule.schedule.make_boilings import make_boilings
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.make_schedule.schedule.parse_start_configuration import parse_start_configuration
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan
from app.scheduler.time_utils import cast_t, cast_time, parse_time


def make_schedule_with_optimal_cleanings(
    boiling_plan_obj,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    exact_start_time_line_name: Optional[str] = LineName.WATER,
    start_configuration=None,
    date=None,
    optimize_cleanings: bool = True,
):
    """
    - Find start_configuration if needed by making a schedule
    - Find optimal cleanings
    - Make schedule with cleanings and start configuration
    - Fix times
    - Reschedule if needed
    Returns
    -------

    """
    logger.info("Making basic schedule")

    schedule = make_schedule_basic(
        boiling_plan_obj=boiling_plan_obj,
        cleanings={},
        start_times=start_times,
        start_configuration=start_configuration,
        exact_start_time_line_name=exact_start_time_line_name,
        date=date,
    )

    configuration = [b.props["boiling_model"].line.name for b in schedule["master"]["boiling", True]]

    # - Find optimal cleanings

    boiling_plan_df = to_boiling_plan(boiling_plan_obj)

    if optimize_cleanings:
        cleanings = _find_optimal_cleanings_combination_by_schedule(schedule)
    else:
        cleanings = boiling_plan_df.groupby("group_id").agg({"cleaning": "first"}).to_dict()["cleaning"]

    # - Make schedule with cleanings and start configuration

    cleanings = {int(k): v for k, v in cleanings.items() if v}
    logger.error(
        "Final schedule using cleanings",
        start_times=start_times,
        cleanings=cleanings,
        configuration=configuration,
    )
    schedule = make_schedule_basic(
        boiling_plan_obj=boiling_plan_obj,
        cleanings=cleanings,
        start_times=start_times,
        start_configuration=configuration,
        exact_start_time_line_name=exact_start_time_line_name,
        date=date,
    )

    # - Return schedule

    return schedule


def test():
    import warnings

    warnings.filterwarnings("ignore")
    from deeplay.utils.loguru_utils.configure_loguru import configure_loguru

    configure_loguru("DEBUG")
    make_schedule_with_optimal_cleanings(
        # str(
        #     get_repo_path()
        #     / "app/data/static/samples/by_department/mozzarella/2023-11-22 План по варкам моцарелла.xlsx"
        # ),
        "/Users/arsenijkadaner/Desktop/моцарелла/2023-11-24 План по варкам моцарелла no water.xlsx",
        start_times={LineName.WATER: "06:00", LineName.SALT: "11:00"},
        exact_start_time_line_name=LineName.SALT,
    )


if __name__ == "__main__":
    test()
