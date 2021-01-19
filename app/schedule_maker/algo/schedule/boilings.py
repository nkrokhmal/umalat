from utils_ak.interactive_imports import *

from app.schedule_maker.algo.boiling import make_boiling
from app.schedule_maker.algo.melting_and_packing import *
from app.enum import LineName


def make_boilings(boiling_plan_df):
    boiling_plan_df = boiling_plan_df.copy()

    res = []

    for boiling_id, grp in boiling_plan_df.groupby('batch_id'):
        boiling_model = grp.iloc[0]['boiling']

        if boiling_model.line.name == LineName.WATER:
            res += make_flow_water_boilings(grp, start_from_id=len(res) + 1)
        else:
            grp['batch_id'] = [len(res) + 1] * len(grp)
            res += make_boilings_parallel_dynamic(grp)
    return res
