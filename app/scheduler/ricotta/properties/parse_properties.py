from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.numeric import is_int_like

from app.scheduler.common.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.common.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.common.parsing_utils.parse_block import parse_elements
from app.scheduler.common.parsing_utils.parse_time_headers import parse_time_headers
from app.scheduler.common.time_utils import cast_t, cast_time
from app.scheduler.ricotta.properties.ricotta_properties import RicottaProperties


def parse_schedule_file(wb_obj):
    # - Load cells

    df = load_cells_df(wb_obj, "Расписание")

    # - Get start times

    time_index_row_nums, start_times = parse_time_headers(cells_df=df)

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
            return is_int_like(row["label"].split(" ")[0]) or "Посолка/анализ" in row["label"]
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
        [4, 6, 8],
        start_time=start_times[0],
        length=100,
        split_func=_split_func,
        filter_=_filter_func,
    )

    parse_elements(
        m,
        df,
        "pouring_offs",
        "pouring_off",
        [6, 8, 10],
        start_time=start_times[0],
        length=100,
        split_func=_split_func,
        filter_=lambda group: "Слив" in group[0]["label"],
    )

    return m.root


def fill_properties(parsed_schedule):
    # - Init properties

    props = RicottaProperties()
    props.is_present = True
    # - Last pumping out time

    pouring_offs = parsed_schedule["pouring_offs"]["pouring_off", True]
    pouring_offs = list(sorted(pouring_offs, key=lambda x: x.y[0]))
    props.last_pumping_out_time = cast_time(pouring_offs[-1].y[0])

    # - Every_5th_pouring_times

    first_rows = parsed_schedule["boiling_first_rows"]["boiling_first_row", True]
    first_rows = sorted(first_rows, key=lambda x: x.y[0])

    props.every_5th_pouring_times = [
        cast_time(row.y[0]) for i, row in enumerate(first_rows) if i % 5 == 4 or i == len(first_rows) - 1
    ]

    # - Last pouring time

    props.last_pouring_time = cast_time(first_rows[-1].y[0])

    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        parse_properties(
            """/Users/marklidenberg/Desktop/inbox/2024.04.06 contour_cleanings/2024-05-28/approved/2024-05-28 Расписание рикотта.xlsx"""
        )
    )


if __name__ == "__main__":
    test()
