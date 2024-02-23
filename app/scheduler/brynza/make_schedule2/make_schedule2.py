import math

from utils_ak.block_tree import AxisPusher, ClassValidator, push, validate_disjoint_by_axis
from utils_ak.block_tree.block_maker import BlockMaker

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.brynza.make_schedule2.make_boiling import make_boiling
from app.scheduler.brynza.make_schedule2.make_salting import make_salting


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


def make_schedule2(
    brynza_kg: int,
    chanah_kg: int,
    start_time="07:00",
    first_batch_ids_by_type: dict = {"brynza": 1},
) -> dict:
    # - Init blockmaker

    m = BlockMaker("schedule")

    # - Make brynza boilings

    current_id = first_batch_ids_by_type["brynza"]
    cheese_maker_id = 0

    for boiling_id in range(math.ceil(int(brynza_kg / 3150)) + 1):
        push(
            m.root,
            make_boiling(
                boiling_id=current_id,
                group_name="Брынза",
                cheese_maker_num=cheese_maker_id + 1,
            ),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1
        cheese_maker_id = (cheese_maker_id + 1) % 4

    # - Make chanah boilings

    for boiling_id in range(math.ceil(int(chanah_kg / 3150)) + 1):
        push(
            m.root,
            make_boiling(
                boiling_id=current_id,
                group_name="Чанах",
                cheese_maker_num=cheese_maker_id + 1,
            ),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1
        cheese_maker_id = (cheese_maker_id + 1) % 4

    # - Make saltings

    current_id = 1
    cheese_maker_id = 0

    for boiling_id in range(math.ceil(int(brynza_kg / 3150)) + 1):
        push(
            m.root,
            make_salting(
                boiling_id=current_id,
                cheese_maker_num=cheese_maker_id + 1,
                group_name="Брынза",
            ),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1
        cheese_maker_id += 1

    return {"schedule": m.root}


def test():
    print(make_schedule2(brynza_kg=10000, chanah_kg=10000))


if __name__ == "__main__":
    test()
