import pandas as pd

from more_itertools import mark_ends
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis

from lessmore.utils.fp import pairwise
from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.mascarpone.make_schedule._make_boiling import _make_boiling
from app.scheduler.mascarpone.to_boiling_plan import BoilingPlanLike, to_boiling_plan
from app.scheduler.time_utils import cast_t


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        if "separation" in b1.children_by_cls and "separation" in b2.children_by_cls:
            validate_disjoint_by_axis(b1["separation"], b2["separation"])

        # todo maybe: refactor [@marklidenberg]
        validate_disjoint_by_axis(b1["pouring"], b2["pouring"])
        if "analysis" in b1.children_by_cls:
            validate_disjoint_by_axis(b1["analysis"], b2["packing_group"])
        if "analysis" in b2.children_by_cls:
            validate_disjoint_by_axis(b1["packing_group"], b2["analysis"])
        if "salting" in b1.children_by_cls and "salting" in b2.children_by_cls:
            validate_disjoint_by_axis(b1["salting"], b2["salting"])
        validate_disjoint_by_axis(b1["packing_group"], b2["packing_group"])
        if "ingredient" in b2.children_by_cls:
            validate_disjoint_by_axis(b1["packing_group"], b2["ingredient"])
        if "heating" in b1.children_by_cls and "heating" in b2.children_by_cls:
            validate_disjoint_by_axis(b1["heating"], b2["heating"])

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        if b2.props["cleaning_object"] in ["pasteurizer", "separator"] and "separation" in b1.children_by_cls:
            validate_disjoint_by_axis(b1["separation"], b2, ordered=True)

        if (
            b2.props["cleaning_object"] == "cream_cheese_tub_1"
            and "separation" in b1.children_by_cls
            and b1.props["group"] == "cream_cheese"
        ):
            validate_disjoint_by_axis(b1["separation"], b2, ordered=True)

    @staticmethod
    def validate__cleaning__boiling(b1, b2):
        if b1.props["cleaning_object"] == "buffer_tank_and_packer" and "separation" in b2.children_by_cls:
            validate_disjoint_by_axis(b1, b2["separation"], ordered=True)

    @staticmethod
    def validate__separator_acceleration__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2["separation"], ordered=True)

    @staticmethod
    def validate__boiling__separator_acceleration(b1, b2):
        validate_disjoint_by_axis(b1["pumping"], b2, ordered=True)  # todo next: check logic [@marklidenberg]

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        if b1.props["contour"] == b2.props["contour"]:
            validate_disjoint_by_axis(b1, b2, distance=1, ordered=True)

        if b2.props["cleaning_object"] == "heat_exchanger":
            validate_disjoint_by_axis(b1, b2, distance=1, ordered=True)


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"cottage_cheese": 1, "cream": 1, "mascarpone": 1, "cream_cheese": 1},
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type).copy()

    # - Init block maker

    m = BlockMaker("schedule")

    # - Make schedule

    # -- Get line

    sample_row = boiling_plan_df.iloc[0]
    line = sample_row["boiling"].line

    # -- Make preparation block

    m.row("preparation", size=6)  # todo next: put to parameters [@marklidenberg]

    # -- Make boiling and packing blocks

    current_group_count = 1

    for is_first, is_last, (prev_indexed_grp, indexed_grp) in mark_ends(
        pairwise(
            boiling_plan_df.groupby("group_id"),
            add_prefix=True,
            add_suffix=True,
        )
    ):
        # - Remove indices

        prev_grp = prev_indexed_grp[1] if prev_indexed_grp else None
        grp = indexed_grp[1] if indexed_grp else None

        # - Calc helpers

        is_new_group = False if (is_first or is_last) else (prev_grp.iloc[0]["group"] != grp.iloc[0]["group"])
        prev_group = None if is_first else prev_grp.iloc[0]["group"]
        group = None if is_last else grp.iloc[0]["group"]

        is_mascarpone_filled = (
            current_group_count >= 3 + 1 and current_group_count % 3 == 1
        ) and prev_group == "mascarpone"

        # - Reset current group count if new group

        if is_new_group:
            current_group_count = 1

        # - Process edge cases

        # -- Separator acceleration

        if is_first and group != "cream" or (prev_group == "cream" and is_new_group):
            # first non-cream of first non-cream after cream
            m.block(
                "separator_acceleration",
                size=(3, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
            )

        # -- Pasteurizer cleaning

        if is_mascarpone_filled or (prev_group == "mascarpone" and is_new_group):
            # add pasteurizer cleaning
            m.block(
                "cleaning",
                size=(19, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                cleaning_object="pasteurizer",
                contour="0",
            )

        # - Full cleaning

        if is_mascarpone_filled or (prev_group == "mascarpone" and is_new_group) or is_last:
            m.block(
                "cleaning",
                size=(13, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                cleaning_object="separator",
                contour="2",
            )

            m.block(
                "cleaning",
                size=(13, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                cleaning_object="tubs",
                contour="2",
            )

            m.block(
                "cleaning",
                size=(13, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                cleaning_object="buffer_tank_and_packer",
                contour="2",
            )

        if prev_group == "cream_cheese" and (is_last or is_new_group):
            m.block(
                "cleaning",
                size=(13, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                cleaning_object="cream_cheese_tub_1",
                contour="1",
            )

        if is_last:
            m.block(
                "cleaning",
                size=(13, 0),
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                cleaning_object="heat_exchanger",
                contour="2",
            )

        if is_last:
            # last element
            continue

        # - Prepare boiling

        boiling = _make_boiling(grp)

        # - Insert new boiling

        m.block(
            boiling,
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
        )

        # - Increment current group count

        current_group_count += 1

    # - Update start time

    m.root.props.update(x=(cast_t(start_time), 0))

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():
    print(
        make_schedule(str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/План по варкам.xlsx"))[
            "schedule"
        ]
    )


if __name__ == "__main__":
    test()
