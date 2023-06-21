from app.imports.runtime import *
from app.scheduler.mozzarella.boiling_plan import read_boiling_plan
from app.scheduler.mozzarella.algo.schedule.make_boilings import make_boilings
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


def get_distance_between_boilings(boiling1: ParallelepipedBlock, boiling2: ParallelepipedBlock):

    # - Init distances

    DISTANCES = []

    # - Create distance collector that will be used to collect distances between blocks (WORKAROUND TO WORK WITH VALIDATOR, which is ugly, but old legacy)

    def distance_collector(b1, b2, axis=0, distance=0, ordered=False):

        # - Get intervals from blocks

        i1 = (b1.x[axis], b1.y[axis])
        i2 = (b2.x[axis], b2.y[axis])

        # - Add neighborhood to the first interval

        i1 = (i1[0] - distance, i1[1] + distance)

        # - Calculate possible distances

        possible_distances = []
        possible_distances.append(i2[0] - i1[1])  # ordered
        if not ordered:
            possible_distances.append(i1[0] - i2[1])  # unordered

        # - Add to output if needed

        DISTANCES.append(max(possible_distances + [0]))

        # - Return

        return max(possible_distances + [0])

    # - Run validation (will collect distances from all checks)

    Validator(block_validator=distance_collector, order_validator=None).validate__boiling__boiling(boiling1, boiling2)

    # - Return actual distance

    return min(DISTANCES)


def test():

    # - Load boilings

    boiling_plan_fn = r"/Users/arsenijkadaner/FileApps/coding_projects/umalat/app/data/static/samples/inputs/by_department/mozzarella/План по варкам моцарелла 2023-06-02.xlsx"
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    boilings = make_boilings(boiling_plan_df)

    # - Get boilings

    b1, b2 = boilings[0], boilings[1]

    # - Change location

    b2.props["x_rel"][0] += 1000

    # - Print distance

    print(get_distance_between_boilings(b1, b2))


if __name__ == "__main__":
    test()
