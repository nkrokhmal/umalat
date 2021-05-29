from app.scheduler.mozzarella.algo.boiling import make_boiling
from app.scheduler.mozzarella.algo.melting_and_packing import *
from app.enum import LineName


def make_boilings(boiling_plan_df, first_boiling_id=None):
    first_boiling_id = first_boiling_id or 1
    boiling_plan_df = boiling_plan_df.copy()

    res = []

    for boiling_id, grp in boiling_plan_df.groupby("group_id"):
        boiling_model = grp.iloc[0]["boiling"]

        if boiling_model.line.name == LineName.WATER:
            boilings = make_flow_water_boilings(
                grp, first_boiling_id=len(res) + first_boiling_id
            )
        else:
            boilings = make_boilings_parallel_dynamic(
                grp, first_boiling_id=len(res) + first_boiling_id
            )

        for boiling in boilings:
            boiling.props.update(boiling_group_df=grp, sheet=grp.iloc[0]["sheet"])
        res += boilings

    return res
