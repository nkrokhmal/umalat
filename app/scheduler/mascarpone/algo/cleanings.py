from utils_ak.block_tree import BlockMaker

from app.models import Washer, cast_model


def make_cleaning(entity, **kwargs):
    m = BlockMaker("cleaning", entity=entity, **kwargs)
    m.row(f"cleaning_{entity}", size=cast_model(Washer, entity).time // 5)
    return m.root
