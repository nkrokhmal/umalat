from utils_ak.interactive_imports import *

from app.schedule_maker.algo.boiling import make_boiling
from app.schedule_maker.algo.melting_and_packing import *
from app.enum import LineName


def make_boilings_basic(boiling_plan_df):
    boiling_plan_df = boiling_plan_df.copy()

    boilings = []

    for boiling_id, boiling_plan in boiling_plan_df.groupby('batch_id'):
        boiling_model = boiling_plan.iloc[0]['boiling']
        melting_and_packing = make_melting_and_packing_basic(boiling_plan)
        boiling = make_boiling(boiling_model, boiling_id, melting_and_packing)
        boilings.append(boiling)
    return boilings


def make_boilings_by_groups(boiling_plan_df):
    boiling_plan_df = boiling_plan_df.copy()
    boiling_plan_df['is_lactose'] = boiling_plan_df['boiling'].apply(lambda boiling: boiling.is_lactose)

    mark_consecutive_groups(boiling_plan_df, 'boiling', 'boiling_group')

    res = []
    for boiling_group, grp in boiling_plan_df.groupby('boiling_group'):
        if grp.iloc[0]['boiling'].line.name == LineName.WATER:
            res += make_flow_water_boilings(grp, start_from_id=len(res) + 1)
        else:
            res += make_boilings_parallel_dynamic(grp)
    return res
