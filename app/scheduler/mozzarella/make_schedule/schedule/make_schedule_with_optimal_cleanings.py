from typing import Optional

from loguru import logger

from app.enum import LineName
from app.scheduler.mozzarella.make_schedule.schedule.find_optimal_cleanings import (
    _find_optimal_cleanings_combination_by_schedule,
)
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def make_schedule_with_optimal_cleanings(
    boiling_plan_obj,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    exact_start_time_line_name: Optional[str] = LineName.WATER,
    start_configuration=None,
    date=None,
    optimize_cleanings: bool = True,
    first_batch_ids_by_type: dict = {"mozzarella": 1},
):

    # - Process case with not optimized cleanings

    if not optimize_cleanings:
        boiling_plan_df = to_boiling_plan(boiling_plan_obj)

        cleanings = boiling_plan_df.groupby("group_id").agg({"cleaning": "first"}).to_dict()["cleaning"]
        cleanings = {int(k): v for k, v in cleanings.items() if v}

        return make_schedule_basic(
            boiling_plan_obj=boiling_plan_obj,
            cleanings=cleanings,
            start_times=start_times,
            start_configuration=start_configuration,
            date=date,
            first_batch_ids_by_type=first_batch_ids_by_type,
        )

    # - Make schedule with no cleanings

    schedule = make_schedule_basic(
        boiling_plan_obj=boiling_plan_obj,
        cleanings={},
        start_times=start_times,
        start_configuration=start_configuration,
        date=date,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )

    # - Get cleanings

    cleanings = _find_optimal_cleanings_combination_by_schedule(schedule)
    cleanings = {int(k): v for k, v in cleanings.items() if v}

    # - Make schedule with cleanings, with configuration from previously built schedule

    logger.info(
        "Using configuration",
        configuration=[b.props["boiling_model"].line.name for b in schedule["master"]["boiling", True]],
    )
    return make_schedule_basic(
        boiling_plan_obj=boiling_plan_obj,
        cleanings=cleanings,
        start_times=start_times,
        start_configuration=[b.props["boiling_model"].line.name for b in schedule["master"]["boiling", True]],
        first_batch_ids_by_type=first_batch_ids_by_type,
        date=date,
    )


def test():
    import warnings

    warnings.filterwarnings("ignore")

    make_schedule_with_optimal_cleanings(
        # str(
        #     get_repo_path()
        #     / "app/data/static/samples/by_department/mozzarella/2023-11-22 План по варкам моцарелла.xlsx"
        # ),
        "/Users/arsenijkadaner/Desktop/моцарелла/2023-11-24 План по варкам моцарелла no water.xlsx",
        start_times={LineName.WATER: "06:00", LineName.SALT: "11:00"},
    )


if __name__ == "__main__":
    test()
