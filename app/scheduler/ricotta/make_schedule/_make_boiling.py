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


def _make_boiling(
    boiling_group_df: pd.DataFrame,
    floculator_num: int,
    drenator_num: int,
    **kwargs,
):
    # - Unfold boiling group params

    sample_row = boiling_group_df.iloc[0]

    boiling_model = sample_row["boiling"]
    technology = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mascarpone department

    # - Init block maker

    m = BlockMaker(
        "boiling",
        boiling_model=boiling_model,
        percent=boiling_model.percent,
        absolute_batch_id=boiling_group_df.iloc[0]["absolute_batch_id"],
        whey_kg=boiling_group_df.iloc[0]["sum_weight_kg"] / boiling_group_df.iloc[0]["floculators_num"],
        kg=boiling_group_df["kg"].sum(),
        **kwargs,
    )

    # - Fill blocks

    # -- Floculators

    current_shift = 0
    for i in range(boiling_group_df.iloc[0]["floculators_num"]):
        with m.push_row(
            "floculator",
            x=current_shift,
            push_func=add_push,
            floculator_num=(floculator_num + i) % 3 + 1,
            output_kg=boiling_group_df.iloc[0]["output_kg"] / 2,  # one boiling is measured in 2 floculators
        ):
            m.push_row("boiling_preparation", size=2)
            pouring = m.push_row("pouring", size=technology.pouring_time // 5).block
            m.push_row("heating", size=technology.heating_time // 5, x=pouring.x[0] - current_shift, push_func=add_push)
            m.push_row("lactic_acid", size=technology.lactic_acid_time // 5)
            m.push_row("draw_whey", size=technology.drain_whey_time // 5)
            m.push_row("dray_ricotta", size=technology.dray_ricotta_time // 5)
        current_shift += technology.pouring_time // 5 + 2

    # - Draw_whey and dray_ricotta should not overlap

    if len(m.root["floculator", True]) > 1:
        b1, b2 = m.root["floculator", True]

        try:
            validate_disjoint_by_axis(b1["dray_ricotta"], b2["draw_whey"], ordered=True)
        except AssertionError as e:
            disposition = json.loads(str(e))["disposition"]

            b2.props.update(x=[b2.props["x_rel"][0] + disposition, b2.x[1]])

    # -- Extra processing: salting, ingredient

    with m.push_row("extra_processing"):
        m.push_row("salting", size=technology.salting_time // 5)
        m.push_row("ingredient", size=technology.ingredient_time // 5)

    # -- Pumping

    pumping = m.push_row(
        "pumping", size=technology.pumping_time // 5 * boiling_group_df.iloc[0]["floculators_num"]
    ).block

    # -- Packing

    packing_minutes = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
    packing_minutes = int(custom_round(a=packing_minutes, b=5, rounding="nearest_half_even", pre_round_precision=1))
    m.push_row(
        "packing",
        size=packing_minutes // 5,
        x=pumping.x[0] + 1,  # 5 minutes after pumping starts
        label="/".join([f"{row['sku'].brand_name} {row['sku'].weight_netto}" for i, row in boiling_group_df.iterrows()])
        + f"  {boiling_group_df.iloc[0]['boiling'].percent}%",
        push_func=add_push,
    )

    return m.root


def test():

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)

    boiling_plan_df = to_boiling_plan(
        str(get_repo_path() / "app/data/static/samples/by_department/ricotta/2024-05-07 Расписание рикотта.xlsx"),
    )
    print(boiling_plan_df)
    boiling_group_df = boiling_plan_df.groupby("batch_id").get_group(1)

    print(_make_boiling(boiling_group_df, floculator_num=0, drenator_num=0))


if __name__ == "__main__":
    test()