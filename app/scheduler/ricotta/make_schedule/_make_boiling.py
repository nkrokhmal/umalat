import warnings

import pandas as pd

from utils_ak.block_tree import add_push, stack_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.dict import dotdict
from utils_ak.numeric.numeric import custom_round
from utils_ak.pandas import mark_consecutive_groups

from app.scheduler.mascarpone.make_schedule.get_packing_switch_size import get_packing_swith_size


warnings.filterwarnings("ignore")


def _make_boiling(boiling_group_df: pd.DataFrame, current_floculator_index: int, **kwargs):
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
        **kwargs,
    )

    # - Fill blocks

    # -- Floculators

    current_shift = 0
    for i in range(boiling_group_df.iloc[0]["floculators_num"]):
        with m.row(
            "floculator",
            x=current_shift,
            push_func=add_push,
            floculator_num=(current_floculator_index + i) % 3 + 1,
        ):
            m.row("boiling_preparation", size=2)
            pouring = m.row("pouring", size=technology.pouring_time // 5).block
            m.row("heating", size=technology.heating_time // 5, x=pouring.x[0] - current_shift, push_func=add_push)
            m.row("lactic_acid", size=technology.lactic_acid_time // 5)
            m.row("draw_whey", size=technology.drain_whey_time // 5)
            m.row("dray_ricotta", size=technology.dray_ricotta_time // 5)
        current_shift += technology.pouring_time // 5 + 2

    # -- Extra processing: salting, ingredient

    with m.row("extra_processing"):
        m.row("salting", size=technology.salting_time // 5)
        m.row("ingredient", size=technology.ingredient_time // 5)

    # -- Pumping

    pumping = m.row("pumping", size=technology.pumping_time // 5 * boiling_group_df.iloc[0]["floculators_num"]).block

    # -- Packing

    packing_minutes = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
    packing_minutes = int(custom_round(packing_minutes, 5, "ceil", pre_round_precision=1))
    m.row(
        "packing",
        size=packing_minutes // 5,
        x=pumping.x[0] + 1,  # 5 minutes after pumping starts
        label="/".join([f"{row['sku'].brand_name} {row['sku'].weight_netto}" for i, row in boiling_group_df.iterrows()])
        + f"  {boiling_group_df.iloc[0]['boiling'].percent}%",
        push_func=add_push,
    )

    return m.root
