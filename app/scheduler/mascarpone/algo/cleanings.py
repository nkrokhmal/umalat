from app.imports.runtime import *

from utils_ak.block_tree import *


def make_cleaning(entity, **kwargs):
    # todo soon: take from models
    CLEANING_SIZES = {
        "sourdough_mascarpone": 13,
        "sourdough_mascarpone_cream_cheese": 12,
        "separator": 15,
        "heat_exchanger": 12,
        "homogenizer": 12,
    }
    m = BlockMaker("cleaning", entity=entity, **kwargs)

    m.row(f"cleaning_{entity}", size=CLEANING_SIZES[entity])

    # todo soon: add steam consumption
    return m.root


def make_container_cleanings():
    m = BlockMaker("container_cleanings")
    m.row("container_cleaning_1", size=12)
    m.row("stub", size=3)
    m.row("container_cleaning_2", size=12)
    m.row("stub", size=3)
    m.row("container_cleaning_3", size=12)
    return m.root
