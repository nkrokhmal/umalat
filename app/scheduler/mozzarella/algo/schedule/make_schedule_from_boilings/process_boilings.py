import pandas as pd


from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boiling import process_boiling
from app.scheduler.shifts import *
from app.enum import LineName
from typing import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def process_boilings(
    m: BlockMaker, # SIDE EFFECTED
    left_df: pd.DataFrame,
    last_multihead_water_boiling: ParallelepipedBlock,
    lines_df: pd.DataFrame,
    cleanings: dict,
    start_configuration: Optional[list],
    shrink_drenators: bool = True,
) -> BlockMaker:

    # - Copy input dataframes to avoid side effects

    left_df = left_df.copy()
    lines_df = lines_df.copy()

    # - Validate start configuration

    assert len(start_configuration) != 0, "Start configuration not specified"

    # - Iterate over boilings and add them to schedule block maker

    cur_boiling_num = 0

    while True:

        # - Check if finished

        if left_df.empty == 0:
            break

        # - Check if only salt left -> start working on 3 line

        if (left_df["line_name"] == LineName.SALT).all():
            lines_df.at[LineName.SALT, "iter_props"] = [
                {"pouring_line": str(v1), "drenator_num": str(v2)} for v1, v2 in itertools.product([2, 3, 1], [0, 1])
            ]

        # - Init iteration variables

        next_rows = [grp.iloc[0] for i, grp in left_df.groupby("sheet")]  # select first rows from each sheet
        cur_lines = len(set([row["line_name"] for row in next_rows]))

        # - Select next row

        if cur_lines == 1:
            # one line of sheet left

            next_row = left_df.iloc[0]
        elif cur_lines == 2:

            # - Filter rows with latest boiling (any boiling is already present for line)

            df = lines_df[~lines_df["latest_boiling"].isnull()]

            # - Select line

            if cur_boiling_num < len(start_configuration):

                # start from specified configuration
                line_name = start_configuration[cur_boiling_num]

                # logger.debug('Chose line by start configuration', line_name=line_name)
            else:

                # choose most latest line
                line_name = max(df["latest_boiling"], key=lambda b: b.x[0]).props["boiling_model"].line.name

                # reverse
                line_name = LineName.WATER if line_name == LineName.SALT else LineName.SALT
                # logger.debug('Chose line by most latest line', line_name=line_name)

            # - Select next row -> first for selected line

            next_row = left_df[left_df["line_name"] == line_name].iloc[0]
        else:
            raise Exception("Should not happen")

        # - Remove newly added row from left rows

        left_df = left_df[left_df["index"] != next_row["index"]]

        # - Disable strict order for non-start confituration blocks

        if cur_boiling_num < len(start_configuration):
            # all configuration blocks should start in strict order

            strict_order = True
        else:
            strict_order = False

        # - Insert boiling

        m = process_boiling(
            m=m, # will be modified inline
            boiling=next_row["boiling"],
            last_multihead_water_boiling=last_multihead_water_boiling,
            lines_df=lines_df,
            cleanings=cleanings,
            shrink_drenators=shrink_drenators,
            strict_order=strict_order,
        )

        # - Iterate cur_boiling_num

        cur_boiling_num += 1

    return m