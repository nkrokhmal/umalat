from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.builtin.collection import delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round


def make_boiling(boiling_model, boiling_id, boiling_volume, melting_and_packing):
    m = BlockMaker("root")

    # - Get boiling technology

    bt = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mozzarella department

    # - Calculate termizator time

    # termizator_time = boiling_model.line.pouring_time * boiling_volume / boiling_model.line.output_kg
    # termizator_time = custom_round(termizator_time, 5, "ceil")
    termizator_time = 25

    # - Push boiling

    with m.push(
        "boiling",
        boiling_id=boiling_id,
        boiling_volume=boiling_volume,
        boiling_model=boiling_model,
    ):
        with m.push("pouring"):
            with m.push("first"):
                m.push_row("termizator", size=termizator_time // 5)
                m.push_row("fermenting", size=bt.pouring_time // 5 - termizator_time // 5)
                m.push_row("soldification", size=bt.soldification_time // 5)
                m.push_row("cutting", size=bt.cutting_time // 5)
                m.push_row("pumping_out", size=bt.pumping_out_time // 5)
            with m.push("second"):
                m.push_row("pouring_off", size=bt.pouring_off_time // 5)
                m.push_row("extra", size=bt.extra_time // 5)
        m.push_row(
            "drenator",
            push_func=add_push,
            x=m.root["boiling"]["pouring"]["first"].y[0],
            size=boiling_model.line.chedderization_time // 5,
        )

    # - Push melting and packing

    push(m.root["boiling"], melting_and_packing)

    # - Return

    return m.root["boiling"]
