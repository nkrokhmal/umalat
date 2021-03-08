from itertools import product
from utils_ak.interactive_imports import *

from app.schedule_maker.algo.packing import (
    get_configuration_time,
    make_configuration_blocks,
)


def fill_configurations(maker, mpps, boiling_model):
    res = [mpps[0]]

    for mpp1, mpp2 in SimpleIterator(mpps).iter_sequences(2):
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
    maker, make = init_block_maker("melting_and_packing", axis=0)

    class_validator = ClassValidator(window=3)

    def validate(b1, b2):
        validate_disjoint_by_axis(b1["melting_process"], b2["melting_process"])
        # validate_disjoint_by_axis(b1['cooling_process']['start'], b2['cooling_process']['start'])

        for p1, p2 in product(b1.iter(cls="packing_team"), b2.iter(cls="packing_team")):
            if p1.props["packing_team_id"] != p2.props["packing_team_id"]:
                continue
            validate_disjoint_by_axis(p1, p2)

    class_validator.add(
        "melting_and_packing_process", "melting_and_packing_process", validate
    )

    def validate(b1, b2):
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

    class_validator.add(
        "melting_and_packing_process", "packing_configuration", validate
    )

    def validate(b1, b2):
        b1, b2 = list(
            sorted([b1, b2], key=lambda b: b.props["cls"])
        )  # melting_and_packing_process, packing_configuration

        packings = list(
            b1.iter(cls="packing", packing_team_id=b2.props["packing_team_id"])
        )
        if not packings:
            return

        for packing in packings:
            validate_disjoint_by_axis(b2, packing)

    class_validator.add(
        "packing_configuration", "melting_and_packing_process", validate
    )

    blocks = fill_configurations(maker, mpps, boiling_model)

    start_from = 0
    for c in blocks:
        if c.props["cls"] == "packing_configuration":
            push(
                maker.root,
                c,
                push_func=lambda parent, block: AxisPusher(start_from="last_end")(
                    parent, block, validator=class_validator
                ),
            )
        else:
            push(
                maker.root,
                c,
                push_func=lambda parent, block: AxisPusher(start_from=start_from)(
                    parent, block, validator=class_validator
                ),
            )
        if c.props["cls"] == "melting_and_packing_process":
            start_from = c["melting_process"].y[0]

    mp = maker.root

    # logger.info('MP', mp=str(mp))
    # print(mp)

    # todo: create warning
    # melting_processes = [block['melting_process'] for block in listify(mp['melting_and_packing_process'])]
    # melting_processes = sorted(melting_processes, key=lambda b: b.x[0])
    # for m1, m2 in SimpleIterator(melting_processes).iter_sequences(2):
    #     assert m1.y[0] == m2.x[0], 'В одной из варок на линии "пицца-чиз" происходит пересол. Это происходит из-за того, что в одной варке подряд стоят форм-факторы разного времени охлаждения: в порядке от большего к меньшему. Чтобы не было пересола нужно указать порядок от меньшего к большему.'

    maker, make = init_block_maker(
        "melting_and_packing", axis=0, make_with_copy_cut=True
    )
    with make("melting"):
        serving = make(
            "serving",
            size=(boiling_model.line.serving_time // 5, 0),
            push_func=add_push,
        ).block

        with make("meltings", x=(serving.size[0], 0), push_func=add_push):
            for i, block in enumerate(listify(mp["melting_and_packing_process"])):

                make(
                    maker.copy(block["melting_process"], with_props=True),
                    bff=block["melting_process"].props["bff"],
                    push_func=add_push,
                )

        with make("coolings", x=(serving.size[0], 0), push_func=add_push):
            for i, block in enumerate(listify(mp["melting_and_packing_process"])):
                make(
                    maker.copy(block["cooling_process"], with_props=True),
                    push_func=add_push,
                )

    for packing_team_id in range(1, 3):  # todo: specify number of teams somewhere
        for key in ["packing", "collecting"]:
            blocks = []

            for mpp in listify(mp["melting_and_packing_process"]):
                for block in listify(mpp[key]):
                    for child_block in block.children:
                        if child_block.props["packing_team_id"] != packing_team_id:
                            continue
                        blocks.append(maker.copy(child_block, with_props=True))

            if "packing_configuration" in [
                block.props["cls"] for block in mp.children
            ]:  # todo: refactor
                for block in [
                    b
                    for b in listify(mp["packing_configuration"])
                    if b.props["packing_team_id"] == packing_team_id
                ]:
                    blocks.append(maker.copy(block, with_props=True))

            if blocks:
                shift = blocks[0].x[0]
                with make(
                    key,
                    x=(boiling_model.line.serving_time // 5 + shift, 0),
                    packing_team_id=packing_team_id,
                    push_func=add_push,
                ):
                    for block in blocks:
                        # fix start with coolings
                        block.props.update(x=(block.props["x_rel"][0] - shift, 0))
                        make(block, push_func=add_push)
    return maker.root
