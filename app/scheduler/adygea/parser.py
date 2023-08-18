# fmt: off
from utils_ak.block_tree import *

from app.imports.runtime import *
from app.scheduler.adygea import *
from app.scheduler.adygea.properties import *
from app.scheduler.parsing import *
from app.scheduler.parsing_new.parse_time import *


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, 'Расписание')

    m = BlockMaker("root")

    with code('Find start times'):
        time_index_row_nums = df[df['label'].astype(str).str.contains('График')]['x1'].unique()

        start_times = []

        for row_num in time_index_row_nums:
            start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))
        # todo maybe: refactor, start_times -> start_ts
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

    parse_block(m, df,
        "boilings",
        "boiling",
        [time_index_row_nums[-1] + i for i in [1, 5, 9, 13]],
        start_times[-1],
        length=100,
        split_func=_split_func,
        filter=_filter_func)

    # parse all blocks at once
    parse_block(m, df,
        "blocks",
        "block",
        [time_index_row_nums[-1] + i for i in [1, 5, 9, 13]],
        start_times[-1],
        length=100,
        split_func=_split_func)
    return m.root


def fill_properties(parsed_schedule):
    props = AdygeaProperties()

    # save boiling_model to parsed_schedule blocks
    boilings = list(sorted(parsed_schedule.iter(cls='boiling'), key=lambda boiling: boiling.y[0]))
    props.n_boilings = len(boilings)
    props.end_time = cast_human_time(parsed_schedule.y[0])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


if __name__ == "__main__":
    # fn = "/Users/marklidenberg/Desktop/2021-09-04 Расписание моцарелла.xlsx"
    fn = '/Users/arsenijkadaner/Desktop/2021-01-02 Расписание милкпроджект-2.xlsx'
    print(dict(parse_properties(fn)))
