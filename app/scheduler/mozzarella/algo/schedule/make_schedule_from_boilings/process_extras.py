from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_termizator_cleaning_block import (
    make_termizator_cleaning_block,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.validator import Validator

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *


def process_extras(
    m: BlockMaker,
):

    # - Push extra packings

    class ExtraValidator(ClassValidator):
        def __init__(self):
            super().__init__(window=10)

        @staticmethod
        def validate__packing__packing(b1, b2):
            return validate_disjoint_by_axis(b1, b2)

        @staticmethod
        def validate__multihead_cleaning__packing(b1, b2):
            multihead_cleaning, packing = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
            for process in packing.iter(cls="process"):
                packer = utils.delistify(process.props["sku"].packers, single=True)
                if packer.name == "Мультиголова":
                    validate_disjoint_by_axis(multihead_cleaning, process, distance=1, ordered=True)

    # - Add multihead to "extra_packings"

    for multihead_cleaning in m.root["extra"].iter(cls="multihead_cleaning"):
        push(m.root["extra_packings"], multihead_cleaning, push_func=add_push)

    # - Add packings to "extra_packings"

    for packing in m.root["extra"].iter(cls="packing"):
        push(
            m.root["extra_packings"],
            packing,
            push_func=AxisPusher(start_from=int(packing.props["extra_props"]["start_from"])),
            validator=ExtraValidator(),
        )

    # - Return

    return m
