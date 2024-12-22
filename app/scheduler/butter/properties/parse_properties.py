import pandas as pd

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.butter.properties.butter_properties import ButterProperties
from app.scheduler.common.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.common.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.common.parsing_utils.parse_block import parse_elements
from app.scheduler.common.parsing_utils.parse_time_headers import parse_time_headers
from app.scheduler.common.time_utils import cast_human_time, cast_t, cast_time


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    # - Get start times

    time_index_row_nums, start_times = parse_time_headers(cells_df=df)

    # - Parse boiling blocks

    m.root.props.update(end_t=df[df["x1"] != 1]["y0"].max() + start_times[0] - 4 - 1)

    parse_elements(m, df, "boilings", "boiling", [time_index_row_nums[0] + 1], start_times[0], length=100)

    # - Parse сепарирование

    parse_elements(
        m,
        df,
        "separations",
        "separation",
        [time_index_row_nums[0] + 1 + i for i in [0, 2]],
        start_times[0],
        length=100,
        split_func=lambda row: "маслообразователь" in row["label"],
        filter_=lambda group: "пастеризация и сепарирование" in group[-1]["label"],
    )

    return m.root


def fill_properties(parsed_schedule):
    props = ButterProperties()
    props.is_present = True

    # save boiling_model to parsed_schedule blocks
    props.end_time = cast_human_time(parsed_schedule.props["end_t"])
    props.separation_end_time = cast_human_time(parsed_schedule["separations"]["separation", True][-1].y[0])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        pd.DataFrame(
            parse_properties(
                # str(get_repo_path() / "app/data/static/samples/by_department/butter/Расписание масло 1.xlsx")
                str(
                    get_repo_path()
                    / "app/data/static/samples/by_day/sample/sample Расписание масло.xlsx"
                )
            )
        )
    )


if __name__ == "__main__":
    test()
