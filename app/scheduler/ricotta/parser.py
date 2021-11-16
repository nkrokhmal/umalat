# fmt: off
from app.imports.runtime import *
from app.scheduler.ricotta import *
from app.scheduler.ricotta.properties import *
from app.scheduler.parsing import *

from utils_ak.block_tree import *



def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, 'Расписание')

    m = BlockMaker("root")

    with code('Find start times'):
        time_index_row_nums = df[df['label'].astype(str).str.contains('График')]['x1'].unique()

        start_times = []

        for row_num in time_index_row_nums:
            hour = int(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"])
            if hour >= 12:
                # yesterday
                hour -= 24
            start_times.append(hour * 12)


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
        [i for i in [3, 7, 11]],
        start_times[0],
        length=4,
        split_func=_split_func,
        filter=_filter_func)

    return m.root


def fill_properties(parsed_schedule):
    props = RicottaProperties()

    # save boiling_model to parsed_schedule blocks
    boilings = list(sorted(parsed_schedule.iter(cls='boiling'), key=lambda boiling: boiling.y[0]))
    props.n_boilings = len(boilings)
    props.last_pumping_out_time = cast_human_time(boilings[-1].y[0])

    if len(boilings) < 9:
        props.start_of_ninth_from_the_end_time = cast_human_time(boilings[-1].x[0])
    else:
        props.start_of_ninth_from_the_end_time = cast_human_time(boilings[-9].x[0])

    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


if __name__ == "__main__":
    # fn = "/Users/marklidenberg/Desktop/2021-09-04 Расписание моцарелла.xlsx"
    fn = '/Users/marklidenberg/Downloads/Telegram Desktop/2021-10-13 Расписание рикотта.xlsx'
    print(dict(parse_properties(fn)))
