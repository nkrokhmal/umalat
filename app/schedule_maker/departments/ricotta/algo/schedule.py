from utils_ak.block_tree import *

from app.schedule_maker.departments.ricotta.algo.boilings import *
from app.schedule_maker.models import *

validator = ClassValidator(window=2)


def validate(b1, b2):
    for line_num in range(3):
        if (
            line_num not in b1.props["line_nums"]
            or line_num not in b2.props["line_nums"]
        ):
            continue

        boiling1 = listify(b1["boiling_sequence"]["boiling"])[
            b1.props["line_nums"].index(line_num)
        ]
        boiling2 = listify(b2["boiling_sequence"]["boiling"])[
            b2.props["line_nums"].index(line_num)
        ]

        validate_disjoint_by_axis(boiling1, boiling2)

    validate_disjoint_by_axis(b1["analysis_group"], b2["analysis_group"])
    validate_disjoint_by_axis(b1["packing"], b2["packing"])


validator.add("boiling_group", "boiling_group", validate)


def make_schedule():
    maker, make = init_block_maker("schedule")

    sku = cast_model(RicottaSKU, 62)  # todo: take from input

    boiling_groups = [make_boiling_group(sku) for _ in range(2)]
    for bg in boiling_groups:
        push(
            maker.root,
            bg,
            push_func=AxisPusher(start_from="last_beg"),
            validator=validator,
            iter_props=[{"line_nums": v} for v in [[0, 1, 2], [1, 2, 0], [2, 0, 1]]],
        )
    return maker.root
