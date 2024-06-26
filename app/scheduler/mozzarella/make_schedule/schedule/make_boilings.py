import collections

from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.enum import LineName
from app.scheduler.mozzarella.make_schedule.schedule.melting_and_packing.pipelines.fluid_flow.water_flow import (
    make_flow_water_boilings,
)
from app.scheduler.mozzarella.make_schedule.schedule.melting_and_packing.pipelines.parallel.parallel import (
    make_boilings_parallel_dynamic,
)
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def make_boilings(boiling_plan_df):
    first_boiling_id = boiling_plan_df["absolute_batch_id"].min()
    boiling_plan_df = boiling_plan_df.copy()

    # - Count boilings per line

    counter = collections.Counter()
    for i, grp in boiling_plan_df.groupby("group_id"):
        counter[grp.iloc[0]["boiling"].line.name] += 1

    # - Make boilings

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
            boiling.props.update(boiling_group_df=grp, group_id=grp.iloc[0]["group_id"], sheet=grp.iloc[0]["sheet"])
        res += boilings

    return res


def test():
    boilings = make_boilings(
        boiling_plan_df=to_boiling_plan(
            "/Users/arsenijkadaner/Desktop/моцарелла/2023-11-22 План по варкам моцарелла.xlsx"
        )
    )
    pass


if __name__ == "__main__":
    test()
