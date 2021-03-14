from utils_ak.iteration import *
from utils_ak.block_tree import *


def make_cleaning(entity, **kwargs):
    # todo: take from models
    CLEANING_SIZES = {
        "sourdough_mascarpone": 13,
        "sourdough_mascarpone_cream_cheese": 12,
        "separator": 15,
        "heat_exchanger": 12,
        "homogenizer": 12,
    }
    maker, make = init_block_maker(
        "cleaning", entity=entity, size=(CLEANING_SIZES[entity], 0), **kwargs
    )

    # todo: add steam consumption
    return maker.root


def make_container_cleanings():
    maker, make = init_block_maker("container_cleanings")
    make("container_cleaning_1", size=(12, 0))
    make("stub", size=(3, 0))
    make("container_cleaning_2", size=(12, 0))
    make("stub", size=(3, 0))
    make("container_cleaning_3", size=(12, 0))
    return maker.root
