# fmt: off

from app.imports.runtime import *
from app.models import *
from app.scheduler.ricotta.algo.boilings import *
from app.scheduler.ricotta.algo.cleanings import *
from app.scheduler.shifts import *
from app.scheduler.time import *


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

            for boiling1 in [boiling for i, boiling in enumerate(b1["boiling_sequence"]["boiling", True]) if b1.props["line_nums"][i] == line_num]:
                for boiling2 in [boiling for i, boiling in enumerate(b2["boiling_sequence"]["boiling", True]) if b2.props["line_nums"][i] == line_num]:
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
            for boiling in [boiling for i, boiling in enumerate(b1["boiling_sequence"]["boiling", True]) if b1.props["line_nums"][i] == line_num]:
                validate_disjoint_by_axis(boiling, bath_cleaning, distance=4, ordered=True)

    @staticmethod
    def validate__boiling_group__container_cleanings(b1, b2):
        # add extra 5 minutes
        _b1 = b1["analysis_group", True][-1]["preparation"]
        _b2 = b2["container_cleaning_1"]
        validate_disjoint_by_axis(_b1, _b2, distance=1, ordered=True)
        validate_disjoint_by_axis(
            b1["analysis_group", True][-1]["analysis"], b2["container_cleaning_2"]
        )
        validate_disjoint_by_axis(
            b1["analysis_group", True][-1]["pumping"], b2["container_cleaning_3"]
        )


def make_schedule(boiling_plan_df,  start_time='07:00'):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()

    boiling_groups = []
    for batch_id, grp in boiling_plan_df.groupby("batch_id"):
        boiling_groups.append(make_boiling_group(grp))
    with code('make_boilings'):
        for bg_prev, bg in utils.iter_pairs(boiling_groups, method="any_prefix"):
            n_tanks = bg.props["n_tanks"]

            first_tank = bg.props["first_tank"]
            line_nums_props = [[0, 1, 2] * 100, [1, 2, 0] * 100, [2, 0, 1] * 100] # allow maximum up to 300 tanks per boiling. Now used 4 maximum (2022.08.29)
            if first_tank:
                # leave only one sequence that fits first_tank
                line_nums_props = line_nums_props[int(first_tank) - 1: int(first_tank)]

            # reorder so that we try to finish at last tank
            idx = -n_tanks % 3 if bg_prev else 0
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

    with code('make_shifts'):
        with m.block("shifts", x=(0, 0), push_func=add_push):
            m.block('meltings')
            m.block('packings')

        with code('meltings'):
            beg = m.root.x[0] - 6 # 0.5h before
            end = m.root.y[0]

            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(m.root['shifts']['meltings'], push_func=add_push,
                     block=m.create_block(
                         "shift",
                         x=(beg, 0),
                         size=(end - beg, 0),
                         shift_num=i
                     ))

        with code('packings'):
            packings = m.root.find(cls='packing')
            beg = packings[0].x[0] - 12 - m.root.x[0]  # 1h before
            end = packings[-1].y[0] + 12 - m.root.x[0]  # 1h after

            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(m.root['shifts']['packings'], push_func=add_push,
                     block=m.create_block(
                         "shift",
                         x=(beg, 0),
                         size=(end - beg, 0),
                         shift_num=i
                     ))
    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
