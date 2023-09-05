import pandas as pd

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis

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

    for i, (boiling_id, grp) in enumerate(boiling_plan_df.groupby("group_id")):
        boiling = _make_boiling(grp)

        m.block(
            boiling,
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
        )

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
