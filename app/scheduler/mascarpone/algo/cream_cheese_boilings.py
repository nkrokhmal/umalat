# fmt: off
# from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_cream_cheese_boiling(boiling_group_df, **props):
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]

    boiling_id = boiling_group_df.iloc[0]["boiling_id"]
    m = BlockMaker(
        "cream_cheese_boiling",
        boiling_model=boiling_model,
        boiling_id=boiling_id,
        **props
    )

    bt = utils.delistify(boiling_model.boiling_technologies, single=True)

    with m.row("boiling_process"):
        m.row("cooling", size=bt.cooling_time // 5)
        m.row("separation", size=bt.separation_time // 5)
        m.row("salting", size=bt.salting_time // 5)
        m.row("separation", size=bt.separation_time // 5)
        m.row("salting", size=bt.salting_time // 5)
        m.row("P", size=bt.p_time // 5)
    with m.row(
        "packing_process", push_func=add_push,
        x=m.root["boiling_process"]["separation"][-1].x[0] - bt.p_time // 5,
    ):
        m.row("P", size=bt.p_time // 5)
        packing_time = sum(
            [
                row["kg"] / row["sku"].packing_speed * 60
                for i, row in boiling_group_df.iterrows()
            ]
        )
        packing_time = int(
            utils.custom_round(packing_time, 5, "ceil", pre_round_precision=1)
        )
        m.row(
            "packing",
            size=packing_time // 5,
        )
    return m.root
