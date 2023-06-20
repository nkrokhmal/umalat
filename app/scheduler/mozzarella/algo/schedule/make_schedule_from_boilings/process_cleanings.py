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

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def process_cleanings(m: BlockMaker) -> BlockMaker:

    # - Add cleanings if necessary

    # -- Extract boilings

    boilings = m.root["master"]["boiling", True]
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))

    # -- Iterate over boilings

    for a, b in utils.iter_pairs(boilings):
        rest = b["pouring"]["first"]["termizator"].x[0] - a["pouring"]["first"]["termizator"].y[0]

        # extract current cleanings
        cleanings = list(m.root["master"].iter(cls="cleaning"))

        # calc in_between and previous cleanings
        in_between_cleanings = [c for c in cleanings if a.x[0] <= c.x[0] <= b.x[0]]

        if not in_between_cleanings:
            # no current in between cleanings -> try to add if needed

            # if rest is more than an hour and less than 80 minutes -> short cleaning
            if rest >= 24:
                cleaning = make_termizator_cleaning_block("short", rule="rest_after_two_hours")
                cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                push(m.root["master"], cleaning, push_func=add_push)

    # - Add last full cleaning

    last_boiling = max(m.root["master"]["boiling", True], key=lambda b: b.y[0])
    start_from = last_boiling["pouring"]["first"]["termizator"].y[0] + 1
    cleaning = make_termizator_cleaning_block("full", rule="closing")  # add five extra minutes
    push(m.root["master"], cleaning, push_func=AxisPusher(start_from=start_from), validator=Validator())

    # - Return

    return m
