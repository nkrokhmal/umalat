import json

import pandas as pd

from more_itertools import first, last, mark_ends
from utils_ak.block_tree import add_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.ricotta.make_schedule._make_boiling import _make_boiling
from app.scheduler.ricotta.to_boiling_plan import to_boiling_plan
from app.scheduler.split_shifts_utils import split_shifts_by_time
from app.scheduler.time_utils import cast_t


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=100)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        f1, f2 = b1["floculator", True][-1], b2["floculator", True][0]
        validate_disjoint_by_axis(f1["pouring"], f2["pouring"])
        if f1.props["floculator_num"] == f2.props["floculator_num"]:
            validate_disjoint_by_axis(f1["draw_whey"], f2["heating"])
        if f1.props["drenator_num"] == f2.props["drenator_num"]:
            validate_disjoint_by_axis(b1["extra_processing"], f2["dray_ricotta"], ordered=True)
        validate_disjoint_by_axis(b1["pumping"], b2["pumping"], distance=2, ordered=True)
        validate_disjoint_by_axis(b1["packing"], b2["packing"], ordered=True)

        if b1.props["percent"] != b2.props["percent"]:
            validate_disjoint_by_axis(b1["packing"], b2["pumping"], ordered=True)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        f1 = b1["floculator", True][-1]
        if b2.props["cleaning_object"] == "floculator" and b1.props["floculator_num"] == b2.props["floculator_num"]:
            validate_disjoint_by_axis(f1["pouring"], b2, ordered=True)

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True, distance=1)


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time="07:00",
    first_batch_ids_by_type: dict = {"ricotta": 1},
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type).copy()

    # - Init block maker

    m = BlockMaker("schedule")

    # - Make preparation block

    m.row(
        "preparation",
        size=6,
        push_func=AxisPusher(start_from=cast_t(start_time)),
        push_kwargs={"validator": Validator()},
    )

    # - Make boilings
    current_floculator_index = 0
    for i, (idx, grp) in enumerate(boiling_plan_df.groupby("batch_id")):
        # - Prepare boiling

        boiling = _make_boiling(grp, current_floculator_index=current_floculator_index)

        # - Insert new boiling

        m.block(
            boiling,
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
            floculator_num=i % 3 + 1,
            drenator_num=i % 2 + 1,
        )

        current_floculator_index += grp.iloc[0]["floculators_num"]

    # - Add cleanings

    for floculator_num in [boiling.props["floculator_num"] for boiling in m.root.iter(cls="boiling")][-3:]:
        m.block(
            "cleaning",
            size=(12, 0),
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
            cleaning_object="floculator",
            floculator_num=floculator_num,
        )

    for cleaning_object in ["drenator", "lishat_richi", "buffer_tank"]:
        m.block(
            "cleaning",
            size=(12, 0),
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
            cleaning_object=cleaning_object,
        )

    # - Make shifts

    # -- Brigadir

    for i, (a, b) in enumerate(
        split_shifts_by_time(
            a=next(m.root.iter(cls="preparation")).y[0],
            b=last(m.root.iter(cls="cleaning", cleaning_object="lishat_richi")).y[0],
            split=cast_t("18:00"),
            min_shift=6,
        )
    ):
        m.block("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="Бригадир", shift_num=i)

    # -- Packing

    for i, (a, b) in enumerate(
        split_shifts_by_time(
            a=first(m.root.iter(cls="packing")).x[0] - 12,
            b=last(m.root.iter(cls="packing")).y[0] + 12,
            split=cast_t("18:00"),
            min_shift=6,
        )
    ):
        m.block("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="Упаковка", shift_num=i)

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():
    # - Configure pandas

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)

    # - Make schedule

    schedule = make_schedule(
        str(get_repo_path() / "app/data/tests/ricotta/boiling.xlsx"),
    )["schedule"]

    print(schedule)


if __name__ == "__main__":
    test()
