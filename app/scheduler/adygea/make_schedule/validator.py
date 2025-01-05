from utils_ak.block_tree.validation.class_validator import ClassValidator
from utils_ak.block_tree.validation.validate_disjoint import validate_disjoint


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint(b1["collecting"], b2["collecting"])

        if b1.props["boiler_num"] == b2.props["boiler_num"]:
            # - Find distance

            is_new_14th_cycle = (
                b2.props["consecutive_num"] >= 15
                and b2.props["consecutive_num"] % 14 in [1, 2, 3, 4]
                and b1.props["group_name"] != "halumi"
            )
            is_addition_changed = b1.props["addition_type"] != b2.props["addition_type"]
            switched_to_chetuk = not b1.props["is_chetuk"] and b2.props["is_chetuk"]
            switched_weight_netto = b1.props["boiling_model"].weight_netto != b2.props["boiling_model"].weight_netto

            if b2.props["group_name"] == "Халуми":
                distance = 0
            else:
                distance = max(
                    0,
                    2 if is_new_14th_cycle else 0,
                    3 if is_addition_changed else 0,
                    2 if switched_to_chetuk else 0,
                    2 if switched_weight_netto else 0,
                )
            validate_disjoint(b1, b2, ordered=True, distance=distance)

        if b2.parent["boiling", True].index(b2) <= 3 and b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint(b1["coagulation"], b2["coagulation"], ordered=True)

        if b1.props["group_name"] == "Халуми" and b2.props["group_name"] == "Халуми":
            validate_disjoint(b1["collecting"], b2["collecting"], ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__lunch(b1, b2):
        if b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        if b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__serum_collection__boiling(b1, b2):
        if b1.props["boiler_num"] != b2.props["boiler_num"]:
            return
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__serum_collection(b1, b2):
        if b1.props["boiler_num"] != b2.props["boiler_num"]:
            return
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__serum_collection__lunch(b1, b2):
        if b1.props["pair_num"] != b2.props["pair_num"]:
            return
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__serum_collection(b1, b2):
        if b1.props["pair_num"] != b2.props["pair_num"]:
            return
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__serum_collection__serum_collection(b1, b2):
        validate_disjoint(b1, b2, ordered=True)
