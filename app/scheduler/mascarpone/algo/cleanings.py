from app.imports.runtime import *

from utils_ak.block_tree import *
from app.models import *


def make_cleaning(entity, **kwargs):
    m = BlockMaker("cleaning", entity=entity, **kwargs)
    m.row(f"cleaning_{entity}", size=cast_model(Washer, entity).time // 5)
    return m.root
