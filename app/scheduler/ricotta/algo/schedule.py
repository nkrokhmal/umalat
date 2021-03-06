# fmt: off

from app.imports.runtime import *

from app.scheduler.ricotta.algo.boilings import *
from app.scheduler.ricotta.algo.cleanings import *
from app.scheduler.time import *
from app.models import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=3)

    @staticmethod
    def validate__boiling_group__boiling_group(b1, b2):
        for line_num in range(3):
            if (
                line_num not in b1.props["line_nums"]
                or line_num not in b2.props["line_nums"]
            ):
                # skip if no common line number is used
                continue

            boiling1 = b1["boiling_sequence"]["boiling", True][b1.props["line_nums"].index(line_num)]
            boiling2 = b2["boiling_sequence"]["boiling", True][b2.props["line_nums"].index(line_num)]

            validate_disjoint_by_axis(boiling1, boiling2)

        validate_disjoint_by_axis(b1["packing"], b2["packing"])

        # five minute pause between bigger to smaller packing size
        sku1 = b1.props["skus"][-1]
        sku2 = b2.props["skus"][0]
        if sku1.weight_netto and sku2.weight_netto and sku1.weight_netto > sku2.weight_netto:
            validate_disjoint_by_axis(b1['packing'], b2['packing'], distance=1, ordered=True)

    @staticmethod
    def validate__boiling_group__bath_cleanings(b1, b2):
        for line_num in range(3):
            bath_cleaning = b2["bath_cleaning", True][line_num]
            if line_num in b1.props["line_nums"]:
                boiling = utils.listify(b1["boiling_sequence"].children)[
                    b1.props["line_nums"].index(line_num)
                ]
                validate_disjoint_by_axis(boiling, bath_cleaning, distance=4, ordered=True)

    @staticmethod
    def validate__boiling_group__container_cleanings(b1, b2):
        # add extra 5 minutes
        _b1 = b1["analysis_group"]["preparation"]
        _b2 = b2["container_cleaning_1"]
        validate_disjoint_by_axis(_b1, _b2, distance=1, ordered=True)
        validate_disjoint_by_axis(
            b1["analysis_group"]["analysis"], b2["container_cleaning_2"]
        )
        validate_disjoint_by_axis(
            b1["analysis_group"]["pumping"], b2["container_cleaning_3"]
        )


def make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00'):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()
    boiling_plan_df["boiling_id"] += first_boiling_id - 1

    boiling_groups = []
    for boiling_id, grp in boiling_plan_df.groupby("boiling_id"):
        boiling_groups.append(make_boiling_group(grp))

    with code('make_boilings'):
        for bg_prev, bg in utils.iter_pairs(boiling_groups, method="any_prefix"):
            n_tanks = bg.props["n_tanks"]
            first_tank = bg.props["first_tank"]

            line_nums_props = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
            if first_tank:
                # leave only one sequence that fits first_tank
                line_nums_props = line_nums_props[int(first_tank) - 1: int(first_tank)]

            # reorder so that we try to finish at last tank
            idx = -n_tanks % 3
            iter_line_nums_props = utils.recycle_list(line_nums_props, idx)

            m.block(bg,
                    push_func=AxisPusher(start_from="last_beg"),
                    push_kwargs={'validator': Validator(),
                                 'iter_props': [{"line_nums": line_nums[:n_tanks]} for line_nums in iter_line_nums_props]})

    with code('make_bath_cleanings'):
        bath_cleanings = make_bath_cleanings()
        m.block(bath_cleanings,
                push_func=AxisPusher(start_from="last_beg"),
                push_kwargs={'validator': Validator()})

    with code('make_container_cleanings'):
        # add container cleanings
        container_cleanings = make_container_cleanings()
        m.block(container_cleanings,
                push_func=AxisPusher(start_from=boiling_groups[-1]["analysis_group"].x[0]),
                push_kwargs={'validator': Validator()})

    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
