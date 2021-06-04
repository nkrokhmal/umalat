from app.imports.runtime import *

from utils_ak.block_tree import *


def make_cleaning(entity, **kwargs):
    # todo later: take from models
    CLEANING_SIZES = {
        "sourdough_mascarpone": 13,
        "sourdough_mascarpone_cream_cheese": 12,
        "separator": 15,
        "heat_exchanger": 12,
        "homogenizer": 12,
    }
    m = BlockMaker("cleaning", entity=entity, **kwargs)

    m.row(f"cleaning_{entity}", size=CLEANING_SIZES[entity])

    return m.root
