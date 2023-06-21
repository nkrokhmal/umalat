from app.scheduler.mozzarella.boiling_plan import *

from .make_schedule_basic import make_schedule_basic
from .start_configuration_optimization import optimize_schedule_by_start_configuration


def make_schedule(
    boiling_plan_obj,
    optimize=True,
    exact_melting_time_by_line=None,
    *args,
    **kwargs,
):
    boiling_plan_df = cast_boiling_plan(boiling_plan_obj, first_batch_id=kwargs.get("first_batch_id", 1))

    if optimize:
        return optimize_schedule_by_start_configuration(
            boiling_plan_df, exact_melting_time_by_line=exact_melting_time_by_line, *args, **kwargs
        )
    else:
        return make_schedule_basic(boiling_plan_df, *args, **kwargs)
