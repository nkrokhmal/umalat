import warnings

from utils_ak.block_tree import add_push, stack_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.dict import dotdict
from utils_ak.numeric.numeric import custom_round
from utils_ak.pandas import mark_consecutive_groups


warnings.filterwarnings("ignore")


def _make_boiling(boiling_group_df, **kwargs):
    # - Unfold boiling group params

    sample_row = boiling_group_df.iloc[0]

    boiling_model = sample_row["boiling"]
    technology = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mascarpone department

    # - Init block maker

    m = BlockMaker(
        "boiling", boiling_model=boiling_model, semifinished_group=sample_row["semifinished_group"], **kwargs
    )

    # - Define scaling factor for cream and apply to technology

    scaling_factor = 1 if sample_row["semifinished_group"] != "cream" else kwargs["input_kg"] / 400
    technology = {
        "separation_time": technology.separation_time,
        "pouring_time": technology.pouring_time,
        "salting_time": technology.salting_time,
        "analysis_time": technology.analysis_time,
        "ingredient_time": technology.ingredient_time,
        "heating_time": technology.heating_time,
        "pumping_time": technology.pumping_time,
    }
    technology = {k: custom_round(v * scaling_factor, 5, rounding="nearest_half_even") for k, v in technology.items()}
    technology = dotdict(technology)

    # - Make pouring

    if technology.separation_time:
        m.row("separation", size=technology.separation_time // 5)

    m.row("pouring", size=technology.pouring_time // 5, push_func=add_push)

    # - Salt if needed

    if technology.salting_time:
        m.row("salting", size=technology.salting_time // 5)

    # - Get packing_group block

    boiling_group_df["weight_netto"] = boiling_group_df["sku"].apply(lambda sku: sku.weight_netto)
    mark_consecutive_groups(boiling_group_df, "weight_netto", "weight_group_id")

    packing_m = BlockMaker()
    with packing_m.block("packing_group"):
        # - Add ingredient if needed

        if technology.analysis_time:
            packing_m.row("analysis", size=technology.analysis_time // 5)
        if technology.ingredient_time:
            packing_m.row("ingredient", size=technology.ingredient_time // 5)

        # - Add packings

        previous_weight = None
        for i, grp in boiling_group_df.groupby("weight_group_id"):
            current_weight = grp.iloc[0]["weight_netto"]

            if previous_weight and current_weight != previous_weight:
                packing_m.row(
                    "packing_switch", size=10 // 5, push_func=stack_push
                )  # todo next: make proper change of packing [@marklidenberg]

            packing_size = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in grp.iterrows()])
            packing_size = int(custom_round(packing_size, 5, "ceil", pre_round_precision=1))
            packing_m.row("packing", size=packing_size // 5, push_func=stack_push)

            previous_weight = current_weight
    packing_group = packing_m.root["packing_group"]

    # - Make other

    if technology.heating_time:
        m.row("heating", size=technology.heating_time // 5)

    current_block = m.row("pumping", size=technology.pumping_time // 5).block

    packing_group.props.update(x=(current_block.x[0] + 5 // 5, 0))
    add_push(m.root, packing_group)

    return m.root
