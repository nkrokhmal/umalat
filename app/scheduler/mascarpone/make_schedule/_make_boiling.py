# todo next: remove [@marklidenberg]
import warnings

from utils_ak.block_tree import add_push, stack_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.numeric.numeric import custom_round
from utils_ak.pandas import mark_consecutive_groups


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

    # - Get packing_group block

    boiling_group_df["weight_netto"] = boiling_group_df["sku"].apply(lambda sku: sku.weight_netto)
    mark_consecutive_groups(boiling_group_df, "weight_netto", "weight_group_id")

    packing_m = BlockMaker()
    with packing_m.block("packing_group"):
        previous_weight = None
        for i, grp in boiling_group_df.groupby("weight_group_id"):
            current_weight = grp.iloc[0]["weight_netto"]

            if previous_weight and current_weight != previous_weight:
                packing_m.row(
                    "packing_switching", size=10 // 5, push_func=stack_push
                )  # todo next: make proper change of packing

            packing_size = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in grp.iterrows()])
            packing_size = int(custom_round(packing_size, 5, "ceil", pre_round_precision=1))

            packing_m.row("packing", size=packing_size, push_func=stack_push)

            previous_weight = current_weight
    packing_group = packing_m.root["packing_group"]

    # - Make other

    if sample_row["group"] == "cream":
        m.row("pumping", size=technology.pumping_time // 5, x=pouring.x[0] + 10 // 5, push_func=add_push)
        analysis = m.row(
            "analysis", size=technology.analysis_time // 5, x=pouring.x[0] + 15 // 5, push_func=add_push
        ).block

        packing_group.props.update(x=(analysis.y[0], 0))
        add_push(m.root, packing_group)

        # m.row("packing", size=packing_size, x=analysis.y[0], push_func=add_push)

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
            packing_group.props.update(x=(current_block.y[0], 0))
            add_push(m.root, packing_group)
            # m.row("packing", size=packing_size, x=current_block.y[0], push_func=add_push)
        else:
            packing_group.props.update(x=(current_block.x[0] + 5 // 5, 0))
            add_push(m.root, packing_group)
            # m.row("packing", size=packing_size, x=current_block.x[0] + 5 // 5, push_func=add_push)

    return m.root
