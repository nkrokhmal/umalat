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

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def create_lines_df(start_times: dict):

    # - Init lines df

    lines_df = pd.DataFrame(
        index=[LineName.WATER, LineName.SALT],
        columns=["iter_props", "start_time", "boilings_left", "latest_boiling"],
    )

    # - Set default values

    lines_df["latest_boiling"] = None

    # - Init iter_props

    lines_df.at[LineName.WATER, "iter_props"] = [
        {"pouring_line": str(v1), "drenator_num": str(v2)} for v1, v2 in itertools.product([0, 1], [0, 1])
    ]
    lines_df.at[LineName.SALT, "iter_props"] = [
        {"pouring_line": str(v1), "drenator_num": str(v2)} for v1, v2 in itertools.product([2, 3], [0, 1])
    ]

    # - Init start times

    for line_name in [LineName.WATER, LineName.SALT]:
        try:
            lines_df.at[line_name, "start_time"] = cast_time(start_times[line_name])
        except:
            raise AssertionError(f"Неверно указано время первой подачи на линии {line_name}")

    # - Check for missing start time

    if lines_df["start_time"].isnull().any():
        missing_lines = lines_df[lines_df["start_time"].isnull()].index
        raise AssertionError(f'Укажите время начала подачи на следующих линиях: {", ".join(missing_lines)}')

    return lines_df
