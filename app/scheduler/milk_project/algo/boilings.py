# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_group_df):
    sample_row = boiling_group_df.iloc[0]
    boiling_model = sample_row['boiling']

    m = BlockMaker("boiling", boiling_model=boiling_model)
    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling model in butter department

    m.row('water_collecting', size=bt.water_collecting_time // 5)
    m.row('mixture_collecting', size=bt.mixture_collecting_time // 5)
    m.row('processing', size=bt.processing_time // 5)
    # todo soon: rename
    m.row('red', size=bt.red_time // 5)
    return m.root
