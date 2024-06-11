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
            if b1.props["boiling_model"].weight_netto != b2.props["boiling_model"].weight_netto:
                validate_disjoint(b1, b2, ordered=True, distance=2)
            else:
                validate_disjoint(b1, b2)

        if b2.parent["boiling", True].index(b2) <= 3 and b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint(b1["coagulation"], b2["coagulation"], ordered=True)

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
