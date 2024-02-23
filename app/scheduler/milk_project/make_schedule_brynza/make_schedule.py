from utils_ak.block_tree import ClassValidator, validate_disjoint_by_axis
from utils_ak.block_tree.block_maker import BlockMaker

from app.lessmore.utils.get_repo_path import get_repo_path


BOILING_NUMS = [0, 2, 1, 3]


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1["collecting"], b2["collecting"])
        if b1.props["boiler_num"] == b2.props["boiler_num"]:
            if b1.props["boiling_model"].weight_netto != b2.props["boiling_model"].weight_netto:
                validate_disjoint_by_axis(b1, b2, ordered=True, distance=2)
            else:
                validate_disjoint_by_axis(b1, b2)

        if b2.parent["boiling", True].index(b2) <= 3 and b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint_by_axis(b1["coagulation"], b2["coagulation"], ordered=True)

    @staticmethod
    def validate__boiling__lunch(b1, b2):
        if b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint_by_axis(b1, b2, ordered=True)

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
    first_batch_ids_by_type: dict = {"milk_project": 1},
) -> dict:
    # - Init blockmaker
    m = BlockMaker("schedule")

    # - Make brynza

    # - Make chanah

    # - Return
    return {"schedule": m.root}


def test():
    print(
        make_schedule(
            str(
                get_repo_path()
                / "app/data/static/samples/by_department/milk_project/План по варкам милкпроджект 3.xlsx"
            )
        )
    )


if __name__ == "__main__":
    test()
