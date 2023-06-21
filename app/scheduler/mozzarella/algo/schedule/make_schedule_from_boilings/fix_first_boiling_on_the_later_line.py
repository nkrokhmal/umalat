from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_termizator_cleaning_block import (
    make_termizator_cleaning_block,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.validator import Validator

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from utils_ak.block_tree import *

from typing import *


def fix_first_boiling_on_the_later_line(
    m: BlockMaker,
    start_configuration: Optional[list],
) -> BlockMaker:

    # - Skip if only one line present

    if len(start_configuration) == 1:
        # only one line present - no need for fix

        return m

    # - Extract boilings and boiling line names

    boilings = list(sorted(m.root["master"]["boiling", True], key=lambda b: b.x[0]))
    boiling_line_names = [b.props["boiling_model"].line.name for b in boilings]

    # - Get first_boiling_of_later_line_index

    index = boiling_line_names.index(start_configuration[-1])

    # - Return if first boiling of later line is last boiling

    if index == len(boilings) - 1:
        # first boiling of later line is last boiling

        return m

    # - Unfold later line boiling and the next one

    b1, b2 = boilings[index], boilings[index + 1]

    # - Fix packing configuration if needed

    boilings_on_line1 = [
        b for b in boilings if b.props["boiling_model"].line.name == b1.props["boiling_model"].line.name
    ]
    index = boilings_on_line1.index(b1)

    if index != len(boilings_on_line1) - 1:

        # not last boiling
        b3 = boilings_on_line1[index + 1]
        with code("Find packing configuration between b2 and b3"):
            packing_configurations = [
                pc
                for pc in m.root["master"]["packing_configuration", True]
                if pc.x[0]
                > b1["melting_and_packing"]["collecting", True][0].x[
                    0
                ]  # todo maybe: we take first collecting here, but this is not very straightforward [@marklidenberg]
                and pc.x[0] <= b3["melting_and_packing"]["collecting", True][0].x[0]
                and pc.props["line_name"] == b1.props["boiling_model"].line.name
            ]

            if packing_configurations:
                pc = utils.delistify(packing_configurations, single=True)
            else:
                pc = None

        with code("Push packing configuration further"):
            if pc:
                max_push = b3["melting_and_packing"]["collecting", True][0].x[0] - pc.x[0]
                pc.detach_from_parent()
                push(
                    m.root["master"],
                    pc,
                    push_func=BackwardsPusher(max_period=max_push),
                    validator=Validator(window=100, sheet_order=False),
                    max_tries=max_push + 1,
                )

    # - Fix boiling

    max_push = b2.x[0] - b1.x[0]
    b1.detach_from_parent()
    push(
        m.root["master"],
        b1,
        push_func=BackwardsPusher(max_period=max_push),
        validator=Validator(window=100, sheet_order=False),
        max_tries=max_push + 1,
    )

    # - Fix order of master blocks

    m.root["master"].reorder_children(lambda b: b.x[0])

    # - Return

    return m
