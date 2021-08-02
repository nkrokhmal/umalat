# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_model, boiler_num):
    m = BlockMaker("boiling", boiling_model=boiling_model, kettle_num=boiler_num)

    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling model in ricotta department

    m.row("collecting", size=bt.collecting_time // 5)
    m.row("coagulation", size=bt.coagulation_time // 5)
    m.row("pouring_off", size=bt.pouring_off_time // 5)

    return m.root
