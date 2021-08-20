# fmt: off

from app.imports.runtime import *
from utils_ak.block_tree import *


def make_bath_cleaning():
    m = BlockMaker("bath_cleaning")
    # todo next: take from models
    m.row("bath_cleaning_1", size=2)
    m.row("bath_cleaning_2", size=4)
    m.row("bath_cleaning_3", size=1)
    m.row("bath_cleaning_4", size=2)
    m.row("bath_cleaning_5", size=2)

    return m.root


def make_bath_cleanings():
    m = BlockMaker("bath_cleanings")

    bath_cleanings = [make_bath_cleaning() for _ in range(3)]

    m.row(bath_cleanings[0])

    for b_prev, b in utils.iter_pairs(bath_cleanings):
        m.row(b, push_func=add_push,
              x=b_prev['bath_cleaning_3'].x)
    return m.root


def make_container_cleanings():
    m = BlockMaker("container_cleanings")
    m.row("container_cleaning_1", size=12)
    m.row("stub", size=3)
    m.row("container_cleaning_2", size=12)
    m.row("stub", size=3)
    m.row("container_cleaning_3", size=12)
    return m.root
