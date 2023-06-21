from app.scheduler.mozzarella.algo.schedule.make_schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.algo.schedule.make_schedule_by_optimizing_start_configuration import (
    make_schedule_by_optimizing_start_configuration,
)
from app.scheduler.mozzarella.boiling_plan import *

from typing import Optional


def make_schedule(
    boiling_plan_obj,
    optimize: bool = True,
    exact_melting_time_by_line=None,
    first_batch_id: int = 1,
    make_schedule_basic_kwargs: Optional[dict] = None,
):
    boiling_plan_df = cast_boiling_plan(boiling_plan_obj, first_batch_id=first_batch_id)

    if optimize:
        return make_schedule_by_optimizing_start_configuration(
            boiling_plan_df,
            exact_melting_time_by_line=exact_melting_time_by_line,
            make_schedule_basic_kwargs=make_schedule_basic_kwargs,
        )
    else:
        return make_schedule_basic(boiling_plan_df, **make_schedule_basic_kwargs)
