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
from app.scheduler.common.time_utils import cast_human_time, cast_t


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    # - Get start times

    time_index_row_nums, start_times = parse_time_headers(cells_df=df)

    # - Parse boiling blocks

    parse_elements(m, df, "boilings", "boiling", [i + 1 for i in time_index_row_nums], start_times[0], length=100)

    return m.root


def fill_properties(parsed_schedule):
    props = ButterProperties()
    props.is_present = True

    # save boiling_model to parsed_schedule blocks
    props.end_time = cast_human_time(parsed_schedule.y[0])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        pd.DataFrame(
            parse_properties(
                str(get_repo_path() / "app/data/static/samples/by_department/butter/Расписание масло 1.xlsx")
            )
        )
    )


if __name__ == "__main__":
    test()
