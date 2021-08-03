# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_model, boiling_id, boiler_num):
    m = BlockMaker("boiling", boiling_model=boiling_model, boiling_id=boiling_id, boiler_num=boiler_num)

    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling model in ricotta department

    m.row("collecting", size=bt.collecting_time // 5)
    m.row("coagulation", size=bt.coagulation_time // 5)
    m.row("pouring_off", size=bt.pouring_off_time // 5)

    return m.root

def make_cleaning(**kwargs):
    m = BlockMaker("cleaning", **kwargs)
    m.row(f"cleaning", size=20)  # todo soon: take from parameters
    return m.root


def make_lunch(**kwargs):
    m = BlockMaker("lunch", **kwargs)
    m.row(f"lunch", size=7)  # todo soon: take from parameters
    return m.root
