from utils_ak.iteration import *
from utils_ak.block_tree import *


def make_bath_cleaning():
    maker, make = init_block_maker("bath_cleaning")

    make("bath_cleaning_1", size=(2, 0))
    make("bath_cleaning_2", size=(4, 0))
    make("bath_cleaning_3", size=(1, 0))
    make("bath_cleaning_4", size=(2, 0))
    make("bath_cleaning_5", size=(2, 0))

    return maker.root


def make_bath_cleaning_sequence():
    maker, make = init_block_maker("bath_cleaning_sequence")

    bath_cleanings = [make_bath_cleaning() for _ in range(3)]

    for b1, b2 in SimpleIterator(bath_cleanings).iter_sequences(2, method="any_prefix"):
        if b1:
            b2.props.update(x=(b1["bath_cleaning_3"].x[0], 0))
        push(maker.root, b2, push_func=add_push)
    return maker.root
