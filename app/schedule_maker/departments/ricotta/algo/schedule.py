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
            # skip if no common line number is used
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

    # five minute pause between bigger to smaller packing size
    sku1 = b1.props["skus"][-1]
    sku2 = b2.props["skus"][0]

    # todo: del
    if sku1.weight_netto and sku2.weight_netto:
        if sku1.weight_netto > sku2.weight_netto:
            assert b1["packing"].y[0] + 1 <= b2["packing"].x[0]


validator.add("boiling_group", "boiling_group", validate)


def _equal_prefixes(lst1, lst2):
    min_len = min(len(lst1), len(lst2))
    return lst1[:min_len] == lst2[:min_len]


def make_schedule(boiling_plan_df):
    maker, make = init_block_maker("schedule")

    boiling_groups = []
    for boiling_id, grp in boiling_plan_df.groupby("boiling_id"):
        boiling_groups.append(make_boiling_group(grp))

    prev_line_nums = None
    for bg_prev, bg in SimpleIterator(boiling_groups).iter_sequences(2, method="any"):
        if not bg:
            # last iteration
            continue

        n_boilings = len(listify(bg["boiling_sequence"]["boiling"]))

        line_nums_props = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        idx = 0
        if bg_prev:
            idx = bg_prev.props["line_nums"][-1]  # ended with number
            idx = (idx + 1) % len(line_nums_props)  # next line_nums in circle
        bg.props.update(line_nums=line_nums_props[idx][:n_boilings])

        push(
            maker.root,
            bg,
            push_func=AxisPusher(start_from="last_beg"),
            validator=validator,
        )
    return maker.root
