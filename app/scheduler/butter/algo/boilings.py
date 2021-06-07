# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_group_df):
    sample_row = boiling_group_df.iloc[0]
    boiling_model = sample_row['boiling']

    m = BlockMaker("boiling", boiling_model=boiling_model)
    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling model in butter department

    m.row('separator_runaway', size=bt.separator_runaway_time // 5)
    m.row('pasteurization_time', size=bt.pasteurization_time // 5)
    m.row('increasing_temperature_time', size=bt.increasing_temperature_time // 5)

    packing_time = sum(
        [
            row["kg"] / row["sku"].packing_speed * 60
            for i, row in boiling_group_df.iterrows()
        ]
    )
    packing_time = int(
        utils.custom_round(packing_time, 5, "ceil", pre_round_precision=1)
    )

    m.row('packing', size=packing_time // 5)
    return m.root
