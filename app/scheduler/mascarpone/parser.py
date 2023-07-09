from app.imports.runtime import *
from app.scheduler.mascarpone import *
from app.scheduler.mascarpone.properties import *
from app.scheduler.parsing import *
from app.scheduler.parsing_new import cast_time_from_hour_label

from utils_ak.block_tree import *


def _is_datetime(v: Union[str, datetime]):
    # main check 09.07.2023 format, but other formats are also possible

    if isinstance(v, datetime):
        return True

    from dateutil.parser import parse

    if len(v) < 8:
        # skip 00, 05, 10, ...
        return False
    try:
        parse(v)
        return True
    except:
        return False


def parse_schedule_file(wb_obj):

    # - Load cells

    df = load_cells_df(wb_obj, "Расписание")

    # - Init block maker

    m = BlockMaker("root")

    # - Find start times
    time_index_row_nums = df[df["label"].astype(str).apply(_is_datetime)]["x1"].unique()
    start_times = []
    for row_num in time_index_row_nums:
        start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))

    # todo maybe: refactor, start_times -> start_ts [@marklidenberg]
    start_times = [cast_t(v) for v in start_times]


    # Precaution for minimum start time
    minimum_start_time = "21:00"
    start_times = [t if t <= cast_t(minimum_start_time) else t - 24 * 12 for t in start_times]

    # - Find boiling groups
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

    parse_block(
        m,
        df,
        "boilings",
        "boiling",
        [time_index_row_nums[0] + 2 + 3 * i for i in range(n_boiling_lines)],
        start_times[0],
        split_func=_split_func,
        filter=_filter_func,
        length=100,
    )

    # - Find fourth_boiling_group_adding_lactic_acid_time

    values = [[boiling, boiling.props["label"], boiling.x[0]] for boiling in m.root["boilings"]["boiling", True]]
    if values:
        df1 = pd.DataFrame(values, columns=["boiling", "label", "start"])
        df1 = df1.sort_values(by="start").reset_index(drop=True)
        df1 = df1.drop_duplicates(subset="label", keep="first")

        if len(df1["label"].unique()) < 4:
            fourth_or_last_label = df1.iloc[-1]["label"]
        else:
            fourth_or_last_label = df1.iloc[3]["label"]
        last_fourth_or_last_boiling = max(
            [
                boiling
                for boiling in m.root["boilings"]["boiling", True]
                if int(boiling.props["label"]) == int(fourth_or_last_label)
            ],
            key=lambda boiling: boiling.x[0],
        )

        # find adding_lactic_acid block (with 4 number on it)
        blocks_df = df[(df["x1"] == int(last_fourth_or_last_boiling.props["row_num"]) + 1) & (df["label"] == "4")]
        blocks_df = blocks_df[blocks_df["x0"] + cast_t(start_times[0]) >= last_fourth_or_last_boiling.x[0]]

        try:
            m.root.props.update(
                fourth_boiling_group_adding_lactic_acid_time=cast_time(blocks_df.iloc[0]["y0"] + start_times[0] - 5)
            )  # don't forget the column header
        except:

            # todo maybe: cream-only case, where there are no 4 labels [@marklidenberg]
            m.root.props.update(fourth_boiling_group_adding_lactic_acid_time=None)

        m.root.props.update(last_pumping_off=m.root.y[0])  # don't forget the column header

    return m.root


def fill_properties(parsed_schedule):
    props = MascarponeProperties()

    # save boiling_model to parsed_schedule blocks
    if parsed_schedule.props["fourth_boiling_group_adding_lactic_acid_time"]:
        props.fourth_boiling_group_adding_lactic_acid_time = cast_human_time(
            parsed_schedule.props["fourth_boiling_group_adding_lactic_acid_time"]
        )
    if parsed_schedule.props["last_pumping_off"]:
        props.last_pumping_off = cast_human_time(parsed_schedule.props["last_pumping_off"])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    fn = "/Users/arsenijkadaner/Downloads/2023-07-09 Расписание маскарпоне.xlsx"
    print(dict(parse_properties(fn)))


if __name__ == "__main__":
    test()
