# fmt: off

from app.imports.runtime import *
from app.scheduler.mozzarella.boiling_plan import *

from utils_ak.block_tree import *

def make_boiling(boiling_model, boiling_id, boiling_volume, melting_and_packing):
    m = BlockMaker("root")

    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling model in mozzarella department
    with m.block(
        "boiling",
        boiling_id=boiling_id,
        boiling_volume=boiling_volume,
        boiling_model=boiling_model,
    ):
        with m.block("pouring"):
            with m.block("first"):
                m.row("termizator", size=boiling_model.line.pouring_time // 5)
                m.row("fermenting", size=bt.pouring_time // 5 - boiling_model.line.pouring_time // 5)
                m.row("soldification", size=bt.soldification_time // 5)
                m.row("cutting", size=bt.cutting_time // 5)
                m.row("pumping_out", size=bt.pumping_out_time // 5)
            with m.block("second"):
                m.row("pouring_off", size=bt.pouring_off_time // 5)
                m.row("extra", size=bt.extra_time // 5)
        m.row("drenator", push_func=add_push,
              x=m.root["boiling"]["pouring"]["first"].y[0],
              size=boiling_model.line.chedderization_time // 5)

        with code('Steam consumption'):
            pass
            # deprecated (2021.06.04). Steam consumption is not needed anymore
            # with m.block("steams"):
            #     m.row("steam_consumption", push_func=add_push,
            #           x=0,
            #           size=6,
            #           value=1100)
            #
            #     if boiling_model.line.name == LineName.SALT:
            #         m.row("steam_consumption", push_func=add_push,
            #               x=m.root["boiling"]["pouring"]["first"]["pumping_out"].x[0] - 3,
            #               size=3,
            #               value=700)

    with code('Steam consumption'):
        pass
        # deprecated (2021.06.04). Steam consumption is not needed anymore
        # add steams to melting_and_packing
        # value = 250 if boiling_model.line.name == LineName.WATER else 1200
        # push(
        #     melting_and_packing,
        #     m.create_block(
        #         "steam_consumption",
        #         size=(melting_and_packing["melting"]["serving"].size[0] + melting_and_packing["melting"]["meltings"].size[0], 0),
        #         value=value,
        #         type="melting",
        #     ),
        #     push_func=add_push,
        # )

    push(m.root["boiling"], melting_and_packing)

    # todo archived: make proper drenator
    # push(maker.root['boiling'], maker.create_block('full_drenator', x=[maker.root['boiling']['pouring']['second']['pouring_off'].x[0], 0], size=[maker.root['drenator'].size[0] + melting_and_packing['melting']['serving'].size[0] + melting_and_packing['melting']['meltings'].size[0], 0]), push_func=add_push)
    return m.root["boiling"]
