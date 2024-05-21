from utils_ak.block_tree import AxisPusher, ClassValidator, push, validate_disjoint_by_axis
from utils_ak.block_tree.block_maker import BlockMaker

from app.scheduler.brynza.make_schedule2.make_boiling import make_boiling
from app.scheduler.brynza.make_schedule2.make_salting import make_salting
from app.scheduler.common.time_utils import cast_t


BOILING_NUMS = [0, 2, 1, 3]


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1["pouring_off"], b2["cutting"], ordered=True)

        if b1.props["cheese_maker_num"] == b2.props["cheese_maker_num"]:
            validate_disjoint_by_axis(b1, b2, ordered=True)

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
    brynza_boilings: int,
    halumi_boilings: int,
    n_cheese_makers: int = 4,
    start_time="07:00",
    first_batch_ids_by_type: dict = {"brynza": 1},
) -> dict:
    # - Init blockmaker

    m = BlockMaker("schedule", x=(cast_t(start_time), 0))

    # - Make brynza boilings

    current_id = first_batch_ids_by_type["brynza"]
    cheese_maker_id = 0

    for boiling_id in range(brynza_boilings):
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
        cheese_maker_id = (cheese_maker_id + 1) % n_cheese_makers

    # - Make halumi boilings

    for boiling_id in range(halumi_boilings):
        push(
            m.root,
            make_boiling(
                boiling_id=current_id,
                group_name="Халуми",
                cheese_maker_num=cheese_maker_id + 1,
            ),
            push_func=AxisPusher(start_from="max_beg"),
            validator=Validator(),
        )
        current_id += 1
        cheese_maker_id = (cheese_maker_id + 1) % n_cheese_makers

    # - Make saltings

    current_id = 1
    cheese_maker_id = 0

    for boiling_id in range(brynza_boilings):
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
    print(make_schedule2(brynza_boilings=3, halumi_boilings=4))


if __name__ == "__main__":
    test()
