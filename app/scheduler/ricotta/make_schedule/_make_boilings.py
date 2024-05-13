import json
import warnings

import pandas as pd

from utils_ak.block_tree import add_push, stack_push, validate_disjoint_by_axis
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.dict import dotdict
from utils_ak.numeric.numeric import custom_round
from utils_ak.pandas import mark_consecutive_groups

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.mascarpone.make_schedule.get_packing_switch_size import get_packing_swith_size
from app.scheduler.ricotta.to_boiling_plan import to_boiling_plan


warnings.filterwarnings("ignore")


def _make_boilings(
    boiling_group_df: pd.DataFrame,
    **kwargs,
):
    # - Unfold boiling group params

    sample_row = boiling_group_df.iloc[0]

    boiling_model = sample_row["boiling"]
    technology = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mascarpone department

    # - Init block maker

    result = []

    # - Calc packing times

    left = sample_row["output_kg"] / 2
    packing_time1 = 0
    packing_time2 = 0

    for i, row in boiling_group_df.iterrows():
        if left > 1e-2:
            if row["kg"] > left:
                packing_time1 += left / row["sku"].packing_speed * 60
                packing_time2 += (row["kg"] - left) / row["sku"].packing_speed * 60
                left = 0
            else:
                packing_time1 += row["kg"] / row["sku"].packing_speed * 60
                left -= row["kg"]
        else:
            packing_time2 += row["kg"] / row["sku"].packing_speed * 60

    packing_times = [packing_time1, packing_time2]  # todo next: kolya: check parameters

    # -- Floculators

    for i in range(boiling_group_df.iloc[0]["floculators_num"]):
        m = BlockMaker(
            "boiling",
            boiling_model=boiling_model,
            percent=boiling_model.percent,
            absolute_batch_id=boiling_group_df.iloc[0]["absolute_batch_id"],
            whey_kg=boiling_group_df.iloc[0]["sum_weight_kg"] / boiling_group_df.iloc[0]["floculators_num"],
            kg=boiling_group_df["kg"].sum(),
            output_kg=boiling_group_df.iloc[0]["output_kg"] / 2,  # one boiling is measured in 2 floculators
            **kwargs,
        )

        m.row("boiling_preparation", size=2)
        pouring = m.row("pouring", size=technology.pouring_time // 5).block
        m.row("heating", size=technology.heating_time // 5, x=pouring.x[0], push_func=add_push)
        m.row("lactic_acid", size=technology.lactic_acid_time // 5)
        m.row("heating_short", size=technology.heating_short_time // 5)
        m.row(
            "draw_whey", size=technology.drain_whey_time // 5
        )  # todo next: kolya: reduce by 5 minutes [@marklidenberg]
        m.row("dray_ricotta", size=technology.dray_ricotta_time // 5)

        # -- Extra processing: salting, ingredient

        with m.row("extra_processing"):
            m.row("salting", size=technology.salting_time // 5)
            m.row("ingredient", size=technology.ingredient_time // 5)  # todo next kolya: fix parameters

        # -- Pumping

        pumping = m.row(
            "pumping",
            size=technology.pumping_time
            // 5,  # todo next: kolya: fix parameters, 25 for non-ingredient, 30 for ingredient. Some formula using speeds? (2 ton/h) [@marklidenberg]
        ).block

        # -- Packing

        packing_size = (
            int(custom_round(a=packing_times[i], b=5, rounding="nearest_half_even", pre_round_precision=1)) // 5
        )

        m.row(
            "packing",
            size=int(custom_round(a=packing_times[i], b=5, rounding="nearest_half_even", pre_round_precision=1)) // 5,
            x=pumping.x[0] + 1
            if packing_size >= pumping.size[0] - 1
            else pumping.y[0] - packing_size,  # 5 minutes after pumping starts
            label="/".join(
                [f"{row['sku'].brand_name} {row['sku'].weight_netto}" for i, row in boiling_group_df.iterrows()]
            )
            + f"  {boiling_group_df.iloc[0]['boiling'].percent}%",
            push_func=add_push,
        )

        result.append(m.root)

    return result


def test():
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)

    boiling_plan_df = to_boiling_plan(
        str(get_repo_path() / "app/data/static/samples/by_department/ricotta/2024-05-07 Расписание рикотта.xlsx"),
    )
    print(boiling_plan_df)
    boiling_group_df = boiling_plan_df.groupby("batch_id").get_group(9)

    print(_make_boilings(boiling_group_df))


if __name__ == "__main__":
    test()
