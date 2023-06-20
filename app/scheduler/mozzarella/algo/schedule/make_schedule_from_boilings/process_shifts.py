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


def process_shifts(m: BlockMaker) -> BlockMaker:

    # - Cheese makers

    beg = min(m.root["master"]["boiling", True], key=lambda b: b.x[0]).x[0] - 6  # 0.5h before start
    end = (
        max(m.root["master"]["boiling", True], key=lambda b: b.y[0])["pouring"]["second"]["pouring_off"].y[0] + 24
    )  # 2h after last pouring off
    shifts = split_shifts(beg, end)

    for i, (beg, end) in enumerate(shifts, 1):
        push(
            m.root["shifts"]["cheese_makers"],
            push_func=add_push,
            block=m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
        )

    # - Water

    water_boilings = [
        b for b in m.root["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
    ]

    if water_boilings:

        # - Water meltings

        beg = water_boilings[0]["melting_and_packing"]["melting"].x[0] - 12  # 1h before start
        end = water_boilings[-1]["melting_and_packing"]["melting"].y[0] + 12  # 1h after end

        shifts = split_shifts(beg, end)

        for i, (beg, end) in enumerate(shifts, 1):
            push(
                m.root["shifts"]["water_meltings"],
                push_func=add_push,
                block=m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
            )

        # - Water packings

        beg = water_boilings[0]["melting_and_packing"]["packing"].x[0] - 18  # 1.5h before start
        end = water_boilings[-1]["melting_and_packing"]["packing"].y[0] + 6  # 0.5h after end

        shifts = split_shifts(beg, end)

        for i, (beg, end) in enumerate(shifts, 1):
            push(
                m.root["shifts"]["water_packings"],
                push_func=add_push,
                block=m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
            )

    # - Salt

    salt_boilings = [
        b for b in m.root["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.SALT
    ]
    if salt_boilings:

        # - Salt meltings

        beg = salt_boilings[0]["melting_and_packing"]["melting"].x[0] - 12  # 1h before start
        end = salt_boilings[-1]["melting_and_packing"]["packing", True][-1].y[0]  # end of packing

        shifts = split_shifts(beg, end)

        for i, (beg, end) in enumerate(shifts, 1):
            push(
                m.root["shifts"]["salt_meltings"],
                push_func=add_push,
                block=m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
            )

        # - Salt packings

        try:
            beg = salt_boilings[0]["melting_and_packing"]["packing", True][0].x[0] - 12  # 1h before start
            end = salt_boilings[-1]["melting_and_packing"]["packing", True][-1].y[0] + 6  # 0.5h after end

            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(
                    m.root["shifts"]["salt_packings"],
                    push_func=add_push,
                    block=m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                )
        except:
            pass

    # - Return

    return m
