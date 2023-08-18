from app.enum.line_name import LineName
from app.scheduler.mozzarella.algo.boiling import make_boiling
from app.scheduler.mozzarella.algo.melting_and_packing import *


def make_boilings(boiling_plan_df):
    first_boiling_id = boiling_plan_df["absolute_batch_id"].min()
    boiling_plan_df = boiling_plan_df.copy()

    with code("Count boilings per line"):
        counter = collections.Counter()
        for i, grp in boiling_plan_df.groupby("group_id"):
            counter[grp.iloc[0]["boiling"].line.name] += 1

    res = []
    res_w = []
    res_s = []

    for boiling_id, grp in boiling_plan_df.groupby("group_id", sort=False):
        boiling_model = grp.iloc[0]["boiling"]

        if boiling_model.line.name == LineName.WATER:
            boilings = make_flow_water_boilings(grp, first_boiling_id=len(res_w) + first_boiling_id)
            res_w += boilings
        else:
            boilings = make_boilings_parallel_dynamic(
                grp,
                first_boiling_id=len(res_s) + first_boiling_id + counter[LineName.WATER],
            )
            res_s += boilings

        for boiling in boilings:
            boiling.props.update(boiling_group_df=grp, sheet=grp.iloc[0]["sheet"])
        res += boilings

    return res
