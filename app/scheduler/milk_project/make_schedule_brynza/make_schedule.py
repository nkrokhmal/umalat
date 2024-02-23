import math

from utils_ak.block_tree import AxisPusher, ClassValidator, push, validate_disjoint_by_axis
from utils_ak.block_tree.block_maker import BlockMaker

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.milk_project.make_schedule_brynza.make_boiling import make_boiling
from app.scheduler.milk_project.make_schedule_brynza.make_salting import make_salting


BOILING_NUMS = [0, 2, 1, 3]


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1["pouring_off"], b2["cutting"], ordered=True)

    @staticmethod
    def validate__boiling__salting(b1, b2):
        validate_disjoint_by_axis(b1["pouring_off"], b2, ordered=True)

    @staticmethod
    def validate__salting__salting(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True, distance=2)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        if b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__lunch(b1, b2):
        pass


def make_schedule(
    brynza_kg: int,
    chanah_kg: int,
    start_time="07:00",
    first_batch_ids_by_type: dict = {"brynza": 1},
) -> dict:
    # - Init blockmaker

    m = BlockMaker("schedule")

    # - Make brynza boilings

    current_id = first_batch_ids_by_type["brynza"]

    for boiling_id in range(math.ceil(int(brynza_kg / 3500))):
        push(
            m.root,
            make_boiling(boiling_id=current_id, group_name="Брынза"),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1

    # - Make chanah boilings

    for boiling_id in range(math.ceil(int(chanah_kg / 3500))):
        push(
            m.root,
            make_boiling(boiling_id=current_id, group_name="Чанах"),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1

    # - Make satlings

    for boiling_id in range(math.ceil(int(brynza_kg / 3500))):
        push(
            m.root,
            make_salting(boiling_id=current_id),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1

    return {"schedule": m.root}


def test():
    print(make_schedule(brynza_kg=10000, chanah_kg=10000))


if __name__ == "__main__":
    test()
