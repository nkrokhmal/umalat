from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.types import is_int_like

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.adygea.properties.adygea_properties import AdygeaProperties
from app.scheduler.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.parsing_utils.parse_block import parse_elements
from app.scheduler.time_utils import cast_human_time, cast_t


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    with code("Find start times"):
        time_index_row_nums = df[df["label"].astype(str).str.contains("График")]["x1"].unique()

        start_times = []

        for row_num in time_index_row_nums:
            start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))

        # todo maybe: refactor, start_times -> start_ts [@marklidenberg]
        start_times = [cast_t(v) for v in start_times]

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
        "boilings",
        "boiling",
        [time_index_row_nums[0] + i for i in [1, 5, 9, 13]],
        start_times[0],
        length=100,
        split_func=_split_func,
        filter_=_filter_func,
    )

    # parse all blocks at once
    parse_elements(
        m,
        df,
        "blocks",
        "block",
        [time_index_row_nums[0] + i for i in [1, 5, 9, 13]],
        start_times[0],
        length=100,
        split_func=_split_func,
    )

    return m.root


def fill_properties(parsed_schedule):
    props = AdygeaProperties()
    props.is_present = True
    # save boiling_model to parsed_schedule blocks
    boilings = list(sorted(parsed_schedule.iter(cls="boiling"), key=lambda boiling: boiling.y[0]))
    props.n_boilings = len(boilings)
    props.end_time = cast_human_time(boilings[-1].y[0])
    return props


def parse_properties(filename):
    parsed_schedule = parse_schedule_file(filename)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        parse_properties(
            """/Users/marklidenberg/Documents/coding/repos/umalat/app/data/dynamic/2024-03-15/approved/2024-03-15 Расписание милкпроджект.xlsx"""
        )
    )


if __name__ == "__main__":
    test()
