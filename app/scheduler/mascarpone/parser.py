# fmt: off
from app.imports.runtime import *
from app.scheduler.mascarpone import *
from app.scheduler.mascarpone.properties import *
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
            if hour >= 15:
                # yesterday
                hour -= 24
            start_times.append(hour * 12)

    n_boiling_lines = (time_index_row_nums[1] - time_index_row_nums[0]) // 3

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
        [time_index_row_nums[0] + 2 + 3 * i for i in range(n_boiling_lines)],
        start_times[0],
        split_func=_split_func,
        filter=_filter_func,
        length=100)

    with code('Find fourth_boiling_group_adding_lactic_acid_time'):
        values = [[boiling, boiling.props['label'], boiling.x[0]] for boiling in m.root['boilings']['boiling', True]]
        if values:
            df1 = pd.DataFrame(values, columns=['boiling', 'label', 'start'])
            df1 = df1.sort_values(by='start').reset_index(drop=True)
            df1 = df1.drop_duplicates(subset='label', keep='first')

            if len(df1['label'].unique()) < 4:
                fourth_or_last_label = df1.iloc[-1]['label']
            else:
                fourth_or_last_label = df1.iloc[3]['label']
            last_fourth_or_last_boiling = max([boiling for boiling in m.root['boilings']['boiling', True] if int(boiling.props['label']) == int(fourth_or_last_label)], key=lambda boiling: boiling.x[0])

            # find adding_lactic_acid block (with 4 number on it)
            blocks_df = df[(df['x1'] == int(last_fourth_or_last_boiling.props['row_num']) + 1) & (df['label'] == '4')]
            blocks_df = blocks_df[blocks_df['x0'] + cast_t(start_times[0]) >= last_fourth_or_last_boiling.x[0]]

            try:
                m.root.props.update(fourth_boiling_group_adding_lactic_acid_time=cast_time(blocks_df.iloc[0]['y0'] + start_times[0] - 5)) # don't forget the column header
            except:
                # todo maybe: cream-only case, where there are no 4 labels
                m.root.props.update(fourth_boiling_group_adding_lactic_acid_time=None)

            m.root.props.update(last_pumping_off=m.root.y[0]) # don't forget the column header

    return m.root


def fill_properties(parsed_schedule):
    props = MascarponeProperties()
    # save boiling_model to parsed_schedule blocks
    if parsed_schedule.props['fourth_boiling_group_adding_lactic_acid_time']:
        props.fourth_boiling_group_adding_lactic_acid_time = cast_human_time(parsed_schedule.props['fourth_boiling_group_adding_lactic_acid_time'])
    if parsed_schedule.props['last_pumping_off']:
        props.last_pumping_off = cast_human_time(parsed_schedule.props['last_pumping_off'])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


if __name__ == "__main__":
    # fn = "/Users/marklidenberg/Desktop/2021-09-04 Расписание моцарелла.xlsx"
    fn = '/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/by_department/mascarpone/Расписание маскарпоне 8.xlsx'
    # fn = '/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/by_department/mascarpone/Расписание маскарпоне 4.xlsx'
    print(dict(parse_properties(fn)))
