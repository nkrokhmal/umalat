from .start_configuration_optimization import optimize_schedule_by_start_configuration
from .schedule_basic import make_schedule_basic
from app.scheduler.mozzarella.boiling_plan import *


def make_schedule(boiling_plan_obj, optimize=True, *args, **kwargs):
    boiling_plan_df = cast_boiling_plan(boiling_plan_obj, first_batch_id=kwargs.get('first_batch_id', 1))

    if optimize:
        return optimize_schedule_by_start_configuration(
            boiling_plan_df, *args, **kwargs
        )
    else:
        return make_schedule_basic(boiling_plan_df, *args, **kwargs)
