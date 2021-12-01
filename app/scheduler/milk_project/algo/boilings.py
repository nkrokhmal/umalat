# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_group_df):
    sample_row = boiling_group_df.iloc[0]
    boiling_model = sample_row['boiling']

    # update 2021.10.21
    m = BlockMaker("boiling", boiling_model=boiling_model, boiling_model_name=boiling_model.name)

    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling modelt

    m.row('mixture_collecting', size=bt.mixture_collecting_time // 5)
    m.row('processing', size=bt.processing_time // 5)
    # todo later: rename
    m.row('red', size=bt.red_time // 5)
    return m.root


def make_boiling_sequence(boilings):
    m = BlockMaker("boiling_sequence")

    sample_boiling_model = boilings[0].props['boiling_model']

    # todo next: switchcom
    # m.row('equipment_check', size=sample_boiling_model.line.equipment_check_time // 5)
    m.row('equipment_check', size=sample_boiling_model.equipment_check_time // 5)
    m.row('water_collecting', size=sample_boiling_model.line.water_collecting_time // 5)

    class Validator(ClassValidator):
        def __init__(self):
            super().__init__(window=1)

        @staticmethod
        def validate__boiling__boiling(b1, b2):
            validate_disjoint_by_axis(b1['processing'], b2['processing'], ordered=True)

        @staticmethod
        def validate__water_collecting__boiling(b1, b2):
            validate_disjoint_by_axis(b1, b2)

    for b in boilings:
        push(m.root, b, push_func=AxisPusher(start_from='last_beg'), validator=Validator())

    return m.root
