from .swap_optimization import optimize_schedule_by_swapping_water_gaps
from app.scheduler.mozzarella.boiling_plan import *


def make_schedule(boiling_plan_obj, *args, **kwargs):
    boiling_plan_df = cast_boiling_plan(boiling_plan_obj)
    return optimize_schedule_by_swapping_water_gaps(boiling_plan_df, *args, **kwargs)
