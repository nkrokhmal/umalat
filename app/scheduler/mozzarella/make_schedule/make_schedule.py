from loguru import logger

from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.make_schedule.schedule.optimize_schedule import optimize_schedule
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def make_schedule(
    boiling_plan: BoilingPlanLike,
    optimize_start_configurations=True,
    optimize_water_gaps=True,
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    # - Make schedule basic kwargs
    optimize_cleanings=False,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    exact_start_time_line_name=None,
    start_configuration=None,
    date=None,
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(
        boiling_plan_source=boiling_plan,
        saturate=saturate,
        normalization=normalization,
        validate=validate,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )

    # - Disable optimizing water gaps if there is only one sheet. It is the case when we upload schedule-file where order is strict

    if len(boiling_plan_df["sheet"].unique()) == 1:
        if optimize_water_gaps or optimize_start_configurations:
            logger.warning("Optimizing is disabled because there is only one sheet in the schedule-file")
            optimize_water_gaps = False
            optimize_start_configurations = False

    # - Make schedule

    if False and optimize_start_configurations or optimize_water_gaps:  # todo next: switch back
        schedule = optimize_schedule(
            boiling_plan_df,
            optimize_start_configurations=optimize_start_configurations,
            optimize_water_gaps=optimize_water_gaps,
            # - Make schedule basic kwargs
            optimize_cleanings=optimize_cleanings,
            start_times=start_times,
            exact_start_time_line_name=exact_start_time_line_name,
            start_configuration=start_configuration,
            date=date,
        )
    else:
        schedule = make_schedule_basic(
            boiling_plan_df,
            start_times=start_times,
            exact_start_time_line_name=exact_start_time_line_name,
            start_configuration=start_configuration,
            date=date,
        )

    # - Return

    return {"schedule": schedule, "boiling_plan_df": boiling_plan_df}


def test():
    print(
        make_schedule(
            str(
                get_repo_path()
                / "app/data/static/samples/by_department/mozzarella/2023-09-22 План по варкам моцарелла.xlsx"
            )
        )
    )


if __name__ == "__main__":
    test()
