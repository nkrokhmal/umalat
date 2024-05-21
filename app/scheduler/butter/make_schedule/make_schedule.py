from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.butter.make_schedule._make_boiling_and_packing import _make_boiling_and_packing
from app.scheduler.butter.to_boiling_plan import BoilingPlanLike, to_boiling_plan
from app.scheduler.common.time_utils import cast_t


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__displacement(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1["pasteurization"], b2["pasteurization"], ordered=True)

    @staticmethod
    def validate__displacement__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__packing(b1, b2):
        if b1.props["is_first"]:
            distance_needed = 0
        else:
            distance_needed = 4  # for cooling

        validate_disjoint_by_axis(b1, b2, ordered=True, distance=distance_needed)

    @staticmethod
    def validate__packing__boiling(b1, b2):
        if b1.props["tank_number"] == b2.props["tank_number"]:
            validate_disjoint_by_axis(b1, b2["pasteurization"], ordered=True, distance=4)

    @staticmethod
    def validate__packing__packing(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True, distance=4)

    @staticmethod
    def validate__packing__displacement(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__packing__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"butter": 1},
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type).copy()

    # - Init block maker

    m = BlockMaker("schedule")

    # - Make schedule

    sample_row = boiling_plan_df.iloc[0]
    line = sample_row["boiling"].line

    # -- Make preparation block

    m.row("preparation", size=line.preparing_time // 5)

    # -- Make boiling and packing blocks

    for i, (boiling_id, grp) in enumerate(boiling_plan_df.groupby("boiling_id")):
        tank_number = i % 2

        boiling, packing = _make_boiling_and_packing(grp, tank_number=tank_number)

        m.block(
            boiling,
            push_func=AxisPusher(start_from="max_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
            is_first=i == 0,
        )
        m.block(
            packing,
            push_func=AxisPusher(start_from="max_beg", start_shift=0),
            push_kwargs={"validator": Validator()},
        )

    # -- Make displacement and cleaning blocks

    m.block(
        m.create_block("displacement", size=(line.displacement_time // 5, 1)),
        push_func=AxisPusher(start_from="max_beg", start_shift=-50),
        push_kwargs={"validator": Validator()},
    )

    # -- Make cleaning block

    m.block(
        m.create_block("cleaning", size=(line.cleaning_time // 5, 1)),
        push_func=AxisPusher(start_from="max_beg", start_shift=-50),
        push_kwargs={"validator": Validator()},
    )

    # - Update start time

    m.root.props.update(x=(cast_t(start_time), 0))

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():
    print(
        make_schedule(
            str(get_repo_path() / "app/data/static/samples/by_department/butter/2023-09-03 План по варкам масло.xlsx")
        )["schedule"]
    )


if __name__ == "__main__":
    test()
