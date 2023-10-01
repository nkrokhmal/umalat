from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.make_schedule.schedule.optimize_schedule_by_start_configuration import (
    optimize_schedule_by_start_configuration,
)
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def make_schedule(
    boiling_plan: BoilingPlanLike,
    optimize=True,
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

    # - Make schedule

    if optimize:
        schedule = optimize_schedule_by_start_configuration(
            boiling_plan_df,
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
