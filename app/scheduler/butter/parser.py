# fmt: off
from app.imports.runtime import *
from app.scheduler.butter import *
from app.scheduler.butter.properties import *
from app.scheduler.parsing import *
from app.scheduler.parsing_new.parse_time import *
from utils_ak.block_tree import *



def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, 'Расписание')

    m = BlockMaker("root")

    with code('Find start times'):
        time_index_row_nums = df[df['label'].astype(str).str.contains('График')]['x1'].unique()

        start_times = []

        for row_num in time_index_row_nums:
            start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))

        # todo maybe: refactor start_times -> start_ts
        start_times = [cast_t(v) for v in start_times]

    parse_block(m, df,
        "boilings",
        "boiling",
        [i + 1 for i in time_index_row_nums],
        start_times[0],
        length=100)

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
    fn = '/Users/marklidenberg/Downloads/Telegram Desktop/2021-10-14 Расписание масло.xlsx'
    print(dict(parse_properties(fn)))
