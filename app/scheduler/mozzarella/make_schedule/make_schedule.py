from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.make_schedule.schedule.optimize_schedule_by_start_configuration import (
    optimize_schedule_by_start_configuration,
)
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def make_schedule(
    boiling_plan: BoilingPlanLike,
    optimize=True,
    exact_melting_time_by_line=None,
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    *args,
    **kwargs,
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
            boiling_plan_df, exact_melting_time_by_line=exact_melting_time_by_line, *args, **kwargs
        )
    else:
        schedule = make_schedule_basic(boiling_plan_df, *args, **kwargs)

    # - Return

    return {"schedule": schedule, "boiling_plan_df": boiling_plan_df}


def test():
    make_schedule(
        str(get_repo_path() / "app/data/static/samples/by_department/mozzarella/2023-09-04 Расписание моцарелла.xlsx")
    )


if __name__ == "__main__":
    test()
