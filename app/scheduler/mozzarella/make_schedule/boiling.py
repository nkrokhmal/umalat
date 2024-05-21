from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.builtin.collection import delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round


def make_boiling(boiling_model, boiling_id, boiling_volume, melting_and_packing):
    m = BlockMaker("root")

    bt = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mozzarella department

    with code("termizator time"):
        termizator_time = boiling_model.line.pouring_time * boiling_volume / boiling_model.line.output_kg
        termizator_time = custom_round(termizator_time, 5, "ceil")

    with m.push(
        "boiling",
        boiling_id=boiling_id,
        boiling_volume=boiling_volume,
        boiling_model=boiling_model,
    ):
        with m.push("pouring"):
            with m.push("first"):
                m.row("termizator", size=termizator_time // 5)
                m.row("fermenting", size=bt.pouring_time // 5 - termizator_time // 5)
                m.row("soldification", size=bt.soldification_time // 5)
                m.row("cutting", size=bt.cutting_time // 5)
                m.row("pumping_out", size=bt.pumping_out_time // 5)
            with m.push("second"):
                m.row("pouring_off", size=bt.pouring_off_time // 5)
                m.row("extra", size=bt.extra_time // 5)
        m.row(
            "drenator",
            push_func=add_push,
            x=m.root["boiling"]["pouring"]["first"].y[0],
            size=boiling_model.line.chedderization_time // 5,
        )

        with code("Steam consumption"):
            pass

    with code("Steam consumption"):
        pass

    push(m.root["boiling"], melting_and_packing)

    # todo archive: make proper drenator
    # push(maker.root['boiling'], maker.create_block('full_drenator', x=[maker.root['boiling']['pouring']['second']['pouring_off'].x[0], 0], size=[maker.root['drenator'].size[0] + melting_and_packing['melting']['serving'].size[0] + melting_and_packing['melting']['meltings'].size[0], 0]), push_func=add_push)
    return m.root["boiling"]
