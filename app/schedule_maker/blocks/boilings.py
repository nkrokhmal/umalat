from utils_ak.interactive_imports import *

from app.schedule_maker.blocks.melting_and_packing import make_melting_and_packing_basic
from app.schedule_maker.blocks.boiling import make_boiling
from app.schedule_maker.blocks.boilings_parallel import make_boilings_parallel_dynamic


def make_boilings_basic(boiling_plan_df):
    boilings = []

    for boiling_id, boiling_plan in boiling_plan_df.groupby('id'):
        boiling_model = boiling_plan.iloc[0]['boiling']

        if boiling_model.boiling_type == 'salt':
            boiling_model.meltings.speed = 850 / 50 * 60

        melting_and_packing = make_melting_and_packing_basic(boiling_plan)
        boiling = make_boiling(boiling_model, boiling_id, melting_and_packing)
        boilings.append(boiling)
    return boilings


def make_boilings_by_groups(boiling_plan_df):
    boiling_plan_df = boiling_plan_df.copy()
    mark_consecutive_groups(boiling_plan_df, 'boiling', 'boiling_group')

    res = []
    for boiling_group, grp in boiling_plan_df.groupby('boiling_group'):
        if grp.iloc[0]['boiling'].boiling_type == 'water':
            res += make_boilings_basic(grp)
        else:
            res += make_boilings_parallel_dynamic(grp)
    return res
