from typing import Callable

import pandas as pd

from more_itertools import last, mark_ends
from utils_ak.block_tree import add_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis
from utils_ak.pandas import mark_consecutive_groups

from lessmore.utils.fp import pairwise
from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.mascarpone.make_schedule._make_boiling import _make_boiling
from app.scheduler.mascarpone.to_boiling_plan import BoilingPlanLike, to_boiling_plan
from app.scheduler.split_shifts_utils import split_shifts_by_time
from app.scheduler.time_utils import cast_t


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        if b1.props["line"] != b2.props["line"]:
            return

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
        if b1.props["line"] != b2.props["line"]:
            return

        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__preparation__separator_acceleration(b1, b2):
        if b1.props["line"] != b2.props["line"]:
            return

        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        if b1.props["line"] != b2.props["line"]:
            return

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
        if b1.props["line"] != b2.props["line"]:
            return

        if b1.props["cleaning_object"] == "buffer_tank_and_packer" and "separation" in b2.children_by_cls:
            validate_disjoint_by_axis(b1, b2["separation"], ordered=True)

    @staticmethod
    def validate__separator_acceleration__boiling(b1, b2):
        if b1.props["line"] != b2.props["line"]:
            return

        validate_disjoint_by_axis(b1, b2["separation"], ordered=True)

    @staticmethod
    def validate__boiling__separator_acceleration(b1, b2):
        if b1.props["line"] != b2.props["line"]:
            return

        validate_disjoint_by_axis(b1["pumping"], b2, ordered=True)  # todo next: check logic [@marklidenberg]

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        if b1.props["contour"] == b2.props["contour"]:
            validate_disjoint_by_axis(b1, b2, distance=1, ordered=True)

        if b2.props["cleaning_object"] == "heat_exchanger":
            validate_disjoint_by_axis(b1, b2, distance=1, ordered=True)


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_times_by_line: dict[int, str] = {1: "07:00", 2: "07:00"},
    first_batch_ids_by_type: dict = {"cottage_cheese": 1, "cream": 1, "mascarpone": 1, "cream_cheese": 1},
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type).copy()

    # - Init block maker

    m = BlockMaker("schedule")

    # - Make schedule by lines

    for line in [1, 2]:
        # -- Filter boiling_plan_df

        boiling_plan_df1 = boiling_plan_df[boiling_plan_df["line"] == line].copy()

        # -- Make preparation block

        m.row("preparation", size=6, line=line, x=cast_t(start_times_by_line[1]), push_func=add_push)

        # -- Make boiling and packing blocks

        current_group_count = 1
        current_group_number = 1
        current_tub_num = 1  # 1 or 2

        for is_first, is_last, (prev_indexed_grp, indexed_grp) in mark_ends(
            pairwise(
                boiling_plan_df1.groupby("group_id"),
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

            if is_new_group or is_mascarpone_filled:
                current_group_number += 1

            # - Process edge cases

            # -- Separator acceleration

            if is_first and group != "cream" or (prev_group == "cream" and is_new_group):
                # first non-cream of first non-cream after cream
                m.block(
                    "separator_acceleration",
                    size=(3, 0),
                    push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                    push_kwargs={"validator": Validator()},
                    line=line,
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
                    line=line,
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
                    line=line,
                )

                m.block(
                    "cleaning",
                    size=(13, 0),
                    push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                    push_kwargs={"validator": Validator()},
                    cleaning_object="tubs",
                    contour="2",
                    line=line,
                )

                m.block(
                    "cleaning",
                    size=(13, 0),
                    push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                    push_kwargs={"validator": Validator()},
                    cleaning_object="buffer_tank_and_packer",
                    contour="2",
                    line=line,
                )

            if prev_group == "cream_cheese" and (is_last or is_new_group):
                m.block(
                    "cleaning",
                    size=(13, 0),
                    push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                    push_kwargs={"validator": Validator()},
                    cleaning_object="cream_cheese_tub_1",
                    contour="1",
                    line=line,
                )

            if prev_group == "robiola" and (is_last or is_new_group):
                m.block(
                    "cleaning",
                    size=(13, 0),
                    push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                    push_kwargs={"validator": Validator()},
                    cleaning_object="cream_cheese_tub_2",
                    contour="1",
                    line=line,
                )

            if is_last:
                m.block(
                    "cleaning",
                    size=(13, 0),
                    push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                    push_kwargs={"validator": Validator()},
                    cleaning_object="heat_exchanger",
                    contour="2",
                    line=line,
                )

            if is_last:
                # last element
                continue

            # - Prepare boiling

            boiling = _make_boiling(grp, tub_num=current_tub_num, group_number=current_group_number, line=line)

            # - Insert new boiling

            m.block(
                boiling,
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
            )

            # - Increment current group count

            current_group_count += 1

            # - Switch tub_num

            if group != "cream":
                current_tub_num = 1 if current_tub_num == 2 else 2

        # - Make boiling_headers

        boilings = list(m.root.iter(cls="boiling", line=line))
        df = pd.DataFrame(boilings, columns=["boiling"])
        df["group"] = df["boiling"].apply(lambda boiling: boiling.props["group"])
        df["group_number"] = df["boiling"].apply(lambda boiling: boiling.props["group_number"])
        for i, grp in df.groupby("group_number"):
            pouring_start = grp.iloc[0]["boiling"]["pouring"].x[0]
            pouring_finish = grp.iloc[-1]["boiling"]["pouring"].y[0]

            if grp.iloc[0]["group"] != "mascarpone":
                m.block(
                    "boiling_header",
                    size=(pouring_finish - pouring_start, 0),
                    x=(pouring_start, 0),
                    push_func=add_push,
                    group=grp.iloc[0]["group"],
                    boilings=grp["boiling"].tolist(),
                    line=line,
                )
            else:
                # shifted 10 minutes to the left. Also add pouring_cream block

                m.block(
                    "boiling_header",
                    size=(pouring_finish - pouring_start, 0),
                    x=(pouring_start - 2, 0),
                    push_func=add_push,
                    group=grp.iloc[0]["group"],
                    boilings=grp["boiling"].tolist(),
                    line=line,
                )

                m.block(
                    "pouring_cream",
                    size=(pouring_finish - pouring_start, 0),
                    x=(pouring_start - 2, 0),
                    push_func=add_push,
                    line=line,
                )

        # - Make shifts

        # -- Brigadir and packer

        shifts = split_shifts_by_time(
            a=next(m.root.iter(cls="preparation", line=line)).x[0],
            b=last(m.root.iter(cls="cleaning", line=line, cleaning_object="buffer_tank_and_packer")).y[0],
            split=cast_t("18:00"),
        )
        for a, b in shifts:
            m.block("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="brigadir", line=line)

            m.block("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="packer", line=line)

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():
    from copy import deepcopy

    schedule = make_schedule(
        str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/План по варкам.xlsx")
    )["schedule"]

    def _filter(b):
        return b.props["cls"] == "preparation"

    def _filter_block(block, cond: Callable):
        if not block.children:
            if cond(block):
                return block
            else:
                return None
        else:
            block.children = [_filter_block(b) for b in block.children]
            block.children = [b for b in block.children if b is not None]
            if not block.children:
                return None
            return block

    print(_filter_block(schedule))


if __name__ == "__main__":
    test()
