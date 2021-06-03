# fmt: off
from app.imports.runtime import *

from app.scheduler.mozzarella.algo.packing import (
    get_configuration_time,
    make_configuration_blocks,
)

from utils_ak.block_tree import *


def fill_configurations(maker, mpps, boiling_model):
    res = [mpps[0]]

    for mpp1, mpp2 in utils.iter_pairs(mpps):
        configuration_blocks = make_configuration_blocks(
            mpp1, mpp2, maker, boiling_model.line.name
        )
        for b in configuration_blocks:
            # reset x position
            b.props.update(x=[0, 0])
        res += configuration_blocks
        res.append(mpp2)
    return res


def make_melting_and_packing_from_mpps(boiling_model, mpps):
    m = BlockMaker("melting_and_packing", axis=0)

    class Validator(ClassValidator):
        def __init__(self):
            super().__init__(window=3)

        @staticmethod
        def validate__melting_and_packing_process__melting_and_packing_process(b1, b2):
            validate_disjoint_by_axis(b1["melting_process"], b2["melting_process"])

            for p1, p2 in itertools.product(
                b1.iter(cls="packing_team"), b2.iter(cls="packing_team")
            ):
                if p1.props["packing_team_id"] != p2.props["packing_team_id"]:
                    continue
                validate_disjoint_by_axis(p1, p2)

        @staticmethod
        def validate__melting_and_packing_process__packing_configuration(b1, b2):
            b1, b2 = list(
                sorted([b1, b2], key=lambda b: b.props["cls"])
            )  # melting_and_packing_process, packing_configuration

            packings = list(
                b1.iter(cls="packing", packing_team_id=b2.props["packing_team_id"])
            )
            if not packings:
                return

            for packing in packings:
                validate_disjoint_by_axis(packing, b2)

        @staticmethod
        def validate__packing_configuration__melting_and_packing_process(b1, b2):
            b1, b2 = list(
                sorted([b1, b2], key=lambda b: b.props["cls"])
            )  # melting_and_packing_process, packing_configuration

            packings = list(
                b1.iter(cls="packing", packing_team_id=b2.props["packing_team_id"])
            )
            if not packings:
                return

            for packing in packings:
                utils.validate_disjoint_by_axis(b2, packing)

    blocks = fill_configurations(m, mpps, boiling_model)

    start_from = 0
    for c in blocks:
        if c.props["cls"] == "packing_configuration":
            m.block(c,
                    push_func=AxisPusher(start_from='last_end'),
                    push_kwargs={'validator': Validator()})
        else:
            m.block(c,
                    push_func=AxisPusher(start_from=start_from),
                    push_kwargs={'validator': Validator()})
        if c.props["cls"] == "melting_and_packing_process":
            start_from = c["melting_process"].y[0]

    mp = m.root

    m = BlockMaker("melting_and_packing", axis=0, make_with_copy_cut=True)
    with m.block("melting"):
        serving = m.row("serving", push_func=add_push,
                        size=boiling_model.line.serving_time // 5).block

        with m.row("meltings",push_func=add_push,
                   x=serving.size[0]):
            for i, block in enumerate(mp["melting_and_packing_process", True]):
                m.block(m.copy(block["melting_process"], with_props=True), push_func=add_push,
                        bff=block["melting_process"].props["bff"])

        with m.row("coolings", push_func=add_push,
                   x=(serving.size[0], 0),):
            for i, block in enumerate(mp["melting_and_packing_process", True]):
                m.block(m.copy(block["cooling_process"], with_props=True), push_func=add_push)

    for packing_team_id in range(1, 3):  # todo: specify number of teams somewhere
        for key in ["packing", "collecting"]:
            blocks = []

            for mpp in mp["melting_and_packing_process", True]:
                for block in mpp[key, True]:
                    for child_block in block.children:
                        if child_block.props["packing_team_id"] != packing_team_id:
                            continue
                        blocks.append(m.copy(child_block, with_props=True))

            if "packing_configuration" in [
                block.props["cls"] for block in mp.children
            ]:  # todo: refactor
                for block in [
                    b
                    for b in mp["packing_configuration", True]
                    if b.props["packing_team_id"] == packing_team_id
                ]:
                    blocks.append(m.copy(block, with_props=True))

            if blocks:
                shift = blocks[0].x[0]
                with m.row(key, push_func=add_push,
                           x=boiling_model.line.serving_time // 5 + shift,
                           packing_team_id=packing_team_id):
                    for block in blocks:
                        # fix start with coolings
                        m.row(block, push_func=add_push,
                              x=block.props["x_rel"][0] - shift)
    return m.root
