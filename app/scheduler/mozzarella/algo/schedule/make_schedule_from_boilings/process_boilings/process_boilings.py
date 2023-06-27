from app.scheduler.mozzarella.algo.schedule.calc_score import calc_score
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boilings.create_left_df import (
    create_left_df,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boilings.create_lines_df import (
    create_lines_df,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boilings.get_last_multihead_water_boiling import (
    get_last_multihead_water_boiling,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boilings.process_boiling import (
    process_boiling,
)
from app.scheduler.shifts import *
from app.enum import LineName
from typing import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def process_boilings(
    m: BlockMaker,  # SIDE EFFECTED
    boilings: List[ParallelepipedBlock],
    start_times: dict,
    cleaning_type_by_group_id: dict,
    start_configuration: Optional[list],
    shrink_drenators: bool = True,
    next_boiling_optimization_type: Literal["chess", "lookahead"] = "chess",
) -> BlockMaker:
    """Process boilings

    Parameters
    ----------
    m : BlockMaker
        BlockMaker to be processed
    boilings : List[ParallelepipedBlock]
        List of boilings to be processed
    start_times : dict
        Start times for each line
    cleaning_type_by_group_id : dict
        Cleaning type by group id
    start_configuration : Optional[list]
        Start configuration
    shrink_drenators : bool, optional
        Shrink drenators, by default True
    next_boiling_optimization : Literal['chess', 'lookahead'], optional
        Next boiling optimization, by default 'lookahead'

        Lookahead - takes longer, optimizes best next boiling by trying to fit [salt, water], [water, salt] and see which is better
        Chess - takes less time, takes other line

    """

    # - Preprocess arguments

    assert next_boiling_optimization_type in [
        "chess",
        "lookahead",
    ], f"Unknown next boiling optimization type: {next_boiling_optimization_type}"

    # - Prepare collaterel variables

    lines_df = create_lines_df(start_times=start_times)

    # - Get left df

    left_df = create_left_df(boilings=boilings)

    # - Get last multihead water boiling

    last_multihead_water_boiling = get_last_multihead_water_boiling(left_df=left_df)

    # - Validate start configuration

    assert len(start_configuration) != 0, "Start configuration not specified"

    # - Iterate over boilings and add them to schedule block maker

    cur_boiling_num = 0

    while True:

        # - Check if finished

        if left_df.empty:
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

            # - Select line

            if cur_boiling_num < len(start_configuration):

                # start from specified configuration
                line_name = start_configuration[cur_boiling_num]

                # logger.debug('Chose line by start configuration', line_name=line_name)
            else:

                if next_boiling_optimization_type == "lookahead":

                    # - Select next line smartly: run WATER, SALT and SALT, WATER. See which one is better - choose line that way

                    water_boiling = left_df[left_df["line_name"] == LineName.WATER].iloc[0]["boiling"]
                    salt_boiling = left_df[left_df["line_name"] == LineName.SALT].iloc[0]["boiling"]

                    # - Generate two lookforward schedules

                    water_schedule = process_boilings(
                        m=copy.deepcopy(m),
                        boilings=[water_boiling, salt_boiling],
                        start_times=start_times,
                        cleaning_type_by_group_id=cleaning_type_by_group_id,
                        start_configuration=[LineName.WATER, LineName.SALT],
                        shrink_drenators=shrink_drenators,
                    ).root

                    water_score = calc_score(water_schedule)
                    salt_schedule = process_boilings(
                        m=copy.deepcopy(m),
                        boilings=[salt_boiling, water_boiling],
                        start_times=start_times,
                        cleaning_type_by_group_id=cleaning_type_by_group_id,
                        start_configuration=[LineName.SALT, LineName.WATER],
                        shrink_drenators=shrink_drenators,
                    ).root
                    salt_score = calc_score(salt_schedule)

                    # - Choose the optimal one

                    line_name = LineName.WATER if water_score < salt_score else LineName.SALT

                elif next_boiling_optimization_type == "chess":

                    # - Filter rows with latest boiling (any boiling is already present for line)

                    df = lines_df[~lines_df["latest_boiling"].isnull()]

                    # - Choose latest line

                    line_name = max(df["latest_boiling"], key=lambda b: b.x[0]).props["boiling_model"].line.name

                    # - Choose reverse line

                    line_name = LineName.WATER if line_name == LineName.SALT else LineName.SALT
                else:
                    raise Exception("Should not happen")

            # - Log

            logger.debug(
                "Chose line", line_name=line_name, next_boiling_optimization_type=next_boiling_optimization_type
            )

            # - Select next row -> first for selected line

            next_row = left_df[left_df["line_name"] == line_name].iloc[0]
        else:
            raise Exception("Should not happen")

        # - Remove newly added row from left rows

        left_df = left_df[left_df["index"] != next_row["index"]]

        # - Enforce strict order for start confituration blocks

        if cur_boiling_num < len(start_configuration):
            # all configuration blocks should start in strict order

            strict_order = True
        else:
            strict_order = False

        # - Insert boiling

        m = process_boiling(
            m=m,  # will be modified inline
            boiling=next_row["boiling"],
            last_multihead_water_boiling=last_multihead_water_boiling,
            lines_df=lines_df,
            cleaning_type_by_group_id=cleaning_type_by_group_id,
            shrink_drenators=shrink_drenators,
            strict_order=strict_order,
        )

        # - Iterate cur_boiling_num

        cur_boiling_num += 1

    # - Return

    return m
