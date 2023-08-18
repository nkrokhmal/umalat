from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.scheduler.butter.properties import ButterProperties
from app.scheduler.parsing import load_cells_df, parse_block
from app.scheduler.parsing_new.parse_time import cast_time_from_hour_label
from app.scheduler.time import cast_human_time, cast_t


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    with code("Find start times"):
        time_index_row_nums = df[df["label"].astype(str).str.contains("График")]["x1"].unique()

        start_times = []

        for row_num in time_index_row_nums:
            start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))

        # todo maybe: refactor start_times -> start_ts
        start_times = [cast_t(v) for v in start_times]

    parse_block(m, df, "boilings", "boiling", [i + 1 for i in time_index_row_nums], start_times[0], length=100)

    return m.root


def fill_properties(parsed_schedule):
    props = ButterProperties()

    # save boiling_model to parsed_schedule blocks
    props.end_time = cast_human_time(parsed_schedule.y[0])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


if __name__ == "__main__":
    # fn = "/Users/marklidenberg/Desktop/2021-09-04 Расписание моцарелла.xlsx"
    fn = "/Users/marklidenberg/Downloads/Telegram Desktop/2021-10-14 Расписание масло.xlsx"
    print(dict(parse_properties(fn)))
