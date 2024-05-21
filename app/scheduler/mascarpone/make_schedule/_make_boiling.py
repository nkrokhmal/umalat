import warnings

from utils_ak.block_tree import add_push, stack_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.dict import dotdict
from utils_ak.numeric.numeric import custom_round
from utils_ak.pandas import mark_consecutive_groups

from app.scheduler.mascarpone.make_schedule.get_packing_switch_size import get_packing_swith_size


warnings.filterwarnings("ignore")


def _make_boiling(boiling_group_df, **kwargs):
    # - Unfold boiling group params

    sample_row = boiling_group_df.iloc[0]

    boiling_model = sample_row["boiling"]

    technology = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mascarpone department

    # - Define scaling factor for cream and apply to technology

    PUMPING_SPEED = 1500  # todo later: put to parameters [@marklidenberg]

    technology = {
        "separation_time": technology.separation_time,
        "pouring_time": technology.pouring_time,
        "salting_time": technology.salting_time,
        "analysis_time": technology.analysis_time,
        "ingredient_time": technology.ingredient_time,
        "heating_time": technology.heating_time,
        "pumping_time": custom_round(
            boiling_group_df["kg"].sum() / PUMPING_SPEED * 60, 5, rounding="nearest_half_even"
        ),
    }
    total_input_kg = (
        boiling_group_df["input_kg"].iloc[0]
        if sample_row["semifinished_group"] != "cream"
        else boiling_group_df["kg"].sum() + 100
    )
    if sample_row["semifinished_group"] == "cream":
        scaling_factor = total_input_kg / 900

        technology["pouring_time"] = custom_round(
            technology["pouring_time"] * scaling_factor, 5, rounding="nearest_half_even"
        )
        technology["pumping_time"] = custom_round(
            technology["pumping_time"] * scaling_factor, 5, rounding="nearest_half_even"
        )

    technology = dotdict(technology)

    # - Init block maker

    m = BlockMaker(
        "boiling",
        boiling_model=boiling_model,
        semifinished_group=sample_row["semifinished_group"],
        kg=boiling_group_df["kg"].sum(),
        total_input_kg=total_input_kg,
        **kwargs,
    )

    # - Make pouring

    if technology.separation_time:
        m.push_row("separation", size=technology.separation_time // 5)

    pouring = m.push_row("pouring", size=technology.pouring_time // 5, push_func=add_push).block

    # - Salt if needed

    if technology.salting_time:
        m.push_row("salting", size=technology.salting_time // 5)

    # - Get packing_group block

    boiling_group_df["weight_netto"] = boiling_group_df["sku"].apply(lambda sku: sku.weight_netto)
    boiling_group_df["sku_name"] = boiling_group_df["sku"].apply(lambda sku: sku.name)
    mark_consecutive_groups(boiling_group_df, key="weight_netto", groups_key="weight_group_id")

    packing_m = BlockMaker()
    with packing_m.push("packing_group"):
        # - Add ingredient if needed

        if technology.analysis_time:
            packing_m.push_row("analysis", size=technology.analysis_time // 5)
        if technology.ingredient_time:
            packing_m.push_row("ingredient", size=technology.ingredient_time // 5)

        # - Add packings

        previous_weight = None
        for i, grp in boiling_group_df.groupby("weight_group_id"):
            current_weight = grp.iloc[0]["weight_netto"]

            if (
                previous_weight
                and current_weight != previous_weight
                and {previous_weight, current_weight} != {0.14, 0.18}
            ):
                packing_m.push_row(
                    "packing_switch",
                    size=get_packing_swith_size(weight_netto1=previous_weight, weight_netto2=current_weight),
                    push_func=stack_push,
                )

            packing_size = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in grp.iterrows()])
            packing_size = int(custom_round(packing_size, 5, "ceil", pre_round_precision=1))
            packing_m.push_row("packing", size=packing_size // 5, push_func=stack_push, weight_netto=current_weight)

            previous_weight = current_weight
    packing_group = packing_m.root["packing_group"]

    # - Make other

    if technology.heating_time:
        m.push_row("heating", size=technology.heating_time // 5)

    if sample_row["semifinished_group"] == "cream":
        current_block = m.push_row(
            "pumping", size=technology.pumping_time // 5, x=pouring.x[0] + 3, push_func=add_push
        ).block
    else:
        current_block = m.push_row("pumping", size=technology.pumping_time // 5).block

    packing_group.props.update(x=(current_block.x[0] + 5 // 5, 0))
    add_push(m.root, packing_group)

    return m.root
