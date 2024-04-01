import pandas as pd

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric import is_int_like

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.parsing_utils.parse_block import parse_elements
from app.scheduler.ricotta.properties.ricotta_properties import RicottaProperties
from app.scheduler.time_utils import cast_human_time, cast_t, cast_time


def parse_schedule_file(wb_obj):
    # - Load cells

    df = load_cells_df(wb_obj, "Расписание")

    # - Init block maker

    m = BlockMaker("root")

    # - Parse

    parse_elements(
        m,
        df,
        "boiling_second_rows",
        "boiling_second_row",
        [i for i in [5, 7, 9]],
        start_time=cast_t(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == 1)].iloc[0]["label"])),
        length=100,
    )

    def _split_func(row):
        try:
            return is_int_like(row["label"].split(" ")[0])
        except:
            return False

    def _filter_func(group):
        try:
            return is_int_like(group[0]["label"].split(" ")[0])
        except:
            return False

    parse_elements(
        m,
        df,
        "boiling_first_rows",
        "boiling_first_row",
        [i for i in [4, 6, 8]],
        start_time=cast_t(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == 1)].iloc[0]["label"])),
        length=100,
        split_func=_split_func,
        filter_=_filter_func,
    )

    return m.root


def fill_properties(parsed_schedule):
    # - Init properties

    props = RicottaProperties()

    # - Last pumping out time

    props.last_pumping_out_time = cast_time(parsed_schedule["boiling_second_rows"]["boiling_second_row", True][-1].y[0])

    # - Every_5th_pouring_times

    first_rows = parsed_schedule["boiling_first_rows"]["boiling_first_row", True]
    first_rows = sorted(first_rows, key=lambda x: x.y[0])

    props.every_5th_pouring_times = [
        cast_time(row.y[0]) for i, row in enumerate(first_rows) if i % 5 == 4 or i == len(first_rows) - 1
    ]

    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        parse_properties(
            """/Users/marklidenberg/Documents/coding/repos/umalat/app/data/dynamic/2024-03-15/approved/2024-03-15 Расписание рикотта.xlsx"""
        )
    )


if __name__ == "__main__":
    test()
