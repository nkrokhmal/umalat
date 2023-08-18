# fmt: off

from utils_ak.block_tree import *

from app.imports.runtime import *
from app.models import *


def make_bath_cleaning():
    m = BlockMaker("bath_cleaning")
    m.row("bath_cleaning_1", size=cast_model(Washer, 'bath_cleaning_1').time // 5)
    m.row("bath_cleaning_2", size=cast_model(Washer, 'bath_cleaning_2').time // 5)
    m.row("bath_cleaning_3", size=cast_model(Washer, 'bath_cleaning_3').time // 5)
    m.row("bath_cleaning_4", size=cast_model(Washer, 'bath_cleaning_4').time // 5)
    m.row("bath_cleaning_5", size=cast_model(Washer, 'bath_cleaning_5').time // 5)

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
