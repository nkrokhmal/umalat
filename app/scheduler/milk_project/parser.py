# fmt: off
from app.imports.runtime import *
from app.scheduler.milk_project import *
from app.scheduler.milk_project.properties import *
from app.scheduler.parsing import *

from utils_ak.block_tree import *


TIME_INDEX_ROW_NUMS = [1]


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, 'Расписание')

    m = BlockMaker("root")

    with code('Find split rows'):
        df1 = df[df['label'] == 'Набор смеси']
        split_rows = df1['x1'].unique()

    with code("fetch start times"):
        start_times = []

        for row_num in TIME_INDEX_ROW_NUMS:
            hour = int(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"])
            if hour >= 12:
                # yesterday
                hour -= 24
            start_times.append(hour * 12)

    def _split_func(row):
        try:
            return row["label"].split(" ")[0] == 'Набор воды в машину'
        except:
            return False

    parse_block(m, df,
        "boilings",
        "boiling",
        [i for i in split_rows],
        start_times[0],
        length=100,
        split_func=_split_func)

    return m.root


def fill_properties(parsed_schedule):
    props = MilkProjectProperties()

    # save boiling_model to parsed_schedule blocks
    boilings = list(sorted(parsed_schedule.iter(cls='boiling'), key=lambda boiling: boiling.y[0]))
    props.n_boilings = len(boilings)
    props.end_time = cast_human_time(boilings[-1].y[0])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


if __name__ == "__main__":
    # fn = "/Users/marklidenberg/Desktop/2021-09-04 Расписание моцарелла.xlsx"
    fn = '/Users/marklidenberg/Downloads/Telegram Desktop/2021-08-25 Расписание милкпроджект.xlsx'
    print(dict(parse_properties(fn)))
