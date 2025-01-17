from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_with_optimal_cleanings import (
    make_schedule_with_optimal_cleanings,
)
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def make_schedule(
    boiling_plan: str,
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    # - Make schedule basic_example kwargs
    optimize_cleanings=False,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
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

    schedule = make_schedule_with_optimal_cleanings(
        boiling_plan_obj=boiling_plan,
        start_times=start_times,
        start_configuration=start_configuration,
        date=date,
        optimize_cleanings=optimize_cleanings,
        first_batch_ids_by_type=first_batch_ids_by_type,
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
