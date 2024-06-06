from collections import Counter
from datetime import datetime
from typing import Union

import pandas as pd

from more_itertools import first, nth
from utils_ak.iteration import iter_pairs

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.common.time_utils import cast_t, cast_time


def _is_datetime(v: Union[str, datetime]):
    # main check 09.07.2023 format, but other formats are also possible

    if isinstance(v, datetime):
        return True

    from dateutil.parser import parse

    if len(v) < 8:
        # skip 00, 05, 10,
        return False
    try:
        parse(v)
        return True
    except:
        return False


def parse_time_headers(cells_df: pd.DataFrame) -> tuple[list, list]:
    """
    Parameters
    ----------
    cells_df: pd.DataFrame
    Cells dataframe, where each row is a cell with columns x0, x1, y0, y1, label

    Returns
    -------
    time_index_row_nums: list
        List of row numbers where time headers are located

    start_times: list
        List of start times for each time header

    """
    # - Find datetime values as a label

    time_index_row_nums = cells_df[cells_df["label"].astype(str).apply(_is_datetime)]["x1"].unique()

    # - For each datetime value, check if header. If so, add to start_time

    start_times = []

    for row_num in time_index_row_nums:
        # - Get values

        values = cells_df[cells_df["x1"] == row_num][
            "label"
        ].values  # "График наливов", "28.05.2024", "30", "35", "40", "45", "50", "55", "1", "05", ...

        # - Filter non-hour label values

        values = [v for v in values if cast_time_from_hour_label(v) is not None]  # "30", "35", ...

        # - Validate that there are lots of 05, 10, 15,

        # we usually draw header with 566 5-minutes intervals, which is ~47 occurences of each 5-minutes interval

        counter = Counter(values)
        if any(
            [
                counter.get(value, 0) <= 20
                for value in ["05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]
            ]
        ):
            continue

        # - Get first value that goes after 55

        first_value_after_55 = first([(a, b) for a, b in iter_pairs(values) if a == "55"], [None, None])[1]  # "1"

        if not first_value_after_55:
            # shoudn't happen, really
            continue

        # - Find the index of this value to correct the start time

        first_value_after_55_index = cells_df[
            (cells_df["label"] == first_value_after_55) & (cells_df["x1"] == row_num)
        ].iloc[0]["x0"]

        # - Get the corrected start time

        start_times.append(
            cast_t(cast_time_from_hour_label(first_value_after_55)) + (5 - first_value_after_55_index)
        )  # 6 (as 30 minutes)

    return list(time_index_row_nums), start_times


def test():
    from app.scheduler.common.parsing_utils.load_cells_df import load_cells_df

    print(
        parse_time_headers(
            load_cells_df(
                wb_obj=str(
                    get_repo_path() / "app/data/static/samples/by_department/mozzarella/sample_schedule_mozzarella.xlsx"
                ),
                sheet_name="Расписание",
            )
        )
    )


if __name__ == "__main__":
    test()
