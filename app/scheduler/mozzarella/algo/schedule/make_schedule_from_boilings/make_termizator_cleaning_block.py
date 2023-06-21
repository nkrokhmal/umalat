from app.imports.runtime import *

from app.scheduler.mozzarella.algo.packing import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    cleaning_name = "Короткая мойка термизатора" if cleaning_type == "short" else "Длинная мойка термизатора"
    washer = cast_model(Washer, cleaning_name)
    m = BlockMaker(
        "cleaning",
        size=(washer.time // 5, 0),
        cleaning_type=cleaning_type,
        **kwargs,
    )
    return m.root