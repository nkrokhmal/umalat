from app.imports.runtime import *
from app.scheduler.mozzarella.boiling_plan import *

from utils_ak.block_tree import *


def make_boiling(boiling_model, boiling_id, boiling_volume, melting_and_packing):

    # - Init block maker

    m = BlockMaker("root")

    # - Get boiling technology

    boiling_technology = utils.delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mozzarella department

    # - Get termizator time

    termizator_time = boiling_model.line.pouring_time * boiling_volume / boiling_model.line.output_ton
    termizator_time = custom_round(termizator_time, 5, "ceil")

    with m.block(
        "boiling",
        boiling_id=boiling_id,
        boiling_volume=boiling_volume,
        boiling_model=boiling_model,
    ):
        with m.block("pouring"):
            with m.block("first"):
                m.row("termizator", size=termizator_time // 5)
                m.row("fermenting", size=boiling_technology.pouring_time // 5 - termizator_time // 5)
                m.row("soldification", size=boiling_technology.soldification_time // 5)
                m.row("cutting", size=boiling_technology.cutting_time // 5)
                m.row("pumping_out", size=boiling_technology.pumping_out_time // 5)
            with m.block("second"):
                m.row("pouring_off", size=boiling_technology.pouring_off_time // 5)
                m.row("extra", size=boiling_technology.extra_time // 5)
        m.row(
            "drenator",
            push_func=add_push,
            x=m.root["boiling"]["pouring"]["first"].y[0],
            size=boiling_model.line.chedderization_time // 5,
        )

    # - Add melting and packing

    push(m.root["boiling"], melting_and_packing)

    # - Return

    return m.root["boiling"]
