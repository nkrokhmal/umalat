import json

import pandas as pd

from more_itertools import last, mark_ends
from utils_ak.block_tree import add_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.ricotta.make_schedule._make_boiling import _make_boiling
from app.scheduler.ricotta.to_boiling_plan import to_boiling_plan


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=100)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1["pouring"], b2["pouring"])

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)


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

    m.row("preparation", size=6)

    # - Make boilings

    for idx, grp in boiling_plan_df.groupby("boiling_id"):

        # - Prepare boiling

        boiling = _make_boiling(grp)

        # - Insert new boiling

        boiling_block = m.block(
            boiling,
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
        ).block

    # # - Add cleanings
    #
    # m.block(
    #     "cleaning",
    #     size=(13, 0),
    #     push_func=AxisPusher(start_from="last_beg", start_shift=-50),
    #     push_kwargs={"validator": Validator()},
    #     cleaning_object="separator",
    #     contour="2",
    #     line=line,
    # )
    #
    # m.block(
    #     "cleaning",
    #     size=(13, 0),
    #     push_func=AxisPusher(start_from="last_beg", start_shift=-50),
    #     push_kwargs={"validator": Validator()},
    #     cleaning_object="tubs",
    #     contour="2",
    #     line=line,
    # )
    #
    # m.block(
    #     "cleaning",
    #     size=(13, 0),
    #     push_func=AxisPusher(start_from="last_beg", start_shift=-50),
    #     push_kwargs={"validator": Validator()},
    #     cleaning_object="buffer_tank_and_packer",
    #     contour="2",
    #     line=line,
    # )
    #
    #     # - Make shifts
    #
    #     shifts = split_shifts_by_time(
    #         a=next(m.root.iter(cls="preparation", line=line)).x[0],
    #         b=last(m.root.iter(cls="cleaning", line=line, cleaning_object="buffer_tank_and_packer")).y[0],
    #         split=cast_t("18:00"),
    #         min_shift=6,
    #     )
    #     for a, b in shifts:
    #         m.block("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="Бригадир", line=line)
    #         m.block("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="Упаковка", line=line)

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():
    # - Configure pandas

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)

    # - Make schedule

    schedule = make_schedule(
        str(get_repo_path() / "app/data/static/samples/by_department/ricotta/boiling.xlsx"),
    )["schedule"]

    print(schedule)


if __name__ == "__main__":
    test()
