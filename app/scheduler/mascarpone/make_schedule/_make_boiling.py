# todo next: remove [@marklidenberg]
import warnings

from utils_ak.block_tree import add_push, stack_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.numeric.numeric import custom_round


warnings.filterwarnings("ignore")


def _make_boiling(boiling_group_df):
    # - Unfold boiling group params

    sample_row = boiling_group_df.iloc[0]

    boiling_model = sample_row["boiling"]
    technology = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mascarpone department

    # todo next: delete [@marklidenberg]
    if "огурцом" in sample_row["sku"].name:
        technology.ingredient_time = 15

    # - Init block maker

    m = BlockMaker("boiling", boiling_model=boiling_model)

    # - Make pouring

    if technology.separation_time:
        m.row("separation", size=technology.separation_time // 5)

    pouring = m.row("pouring", size=technology.pouring_time // 5, push_func=add_push).block

    # - Salt if needed

    if technology.salting_time:
        m.row("salting", size=technology.salting_time // 5)

    # - Calc packing time

    packing_size = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
    packing_size = int(custom_round(packing_size, 5, "ceil", pre_round_precision=1))

    # - Make other

    if sample_row["group"] == "cream":
        m.row("pumping", size=technology.pumping_time // 5, x=pouring.x[0] + 10 // 5, push_func=add_push)
        analysis = m.row(
            "analysis", size=technology.analysis_time // 5, x=pouring.x[0] + 15 // 5, push_func=add_push
        ).block
        m.row("packing", size=packing_size, x=analysis.y[0], push_func=add_push)

    else:
        if technology.heating_time:
            m.row("heating", size=technology.heating_time // 5)

        current_block = m.row("pumping", size=technology.pumping_time // 5).block

        if technology.ingredient_time:
            current_block = m.row(
                "ingredient",
                size=technology.ingredient_time // 5,
                x=current_block.x[0] + 10 // 5,
                push_func=add_push,
            ).block
            m.row("packing", size=packing_size, x=current_block.y[0], push_func=add_push)
        else:
            m.row("packing", size=packing_size, x=current_block.x[0] + 5 // 5, push_func=add_push)

    return m.root
