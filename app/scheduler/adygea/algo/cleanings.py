from app.imports.runtime import *

from utils_ak.block_tree import *


def make_cleaning(**kwargs):
    m = BlockMaker("cleaning", **kwargs)
    m.row(f"cleaning", size=20)  # todo soon: take from parameters
    return m.root
