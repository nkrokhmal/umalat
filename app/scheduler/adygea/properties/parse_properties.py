from app.lessmore.utils.get_repo_path import get_repo_path
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.types import is_int_like

from app.scheduler.adygea.properties.adygea_properties import AdygeaProperties
from app.scheduler.common.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.common.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.common.parsing_utils.parse_block import parse_elements
from app.scheduler.common.parsing_utils.parse_time_headers import parse_time_headers
from app.scheduler.common.time_utils import cast_human_time, cast_t


def parse_schedule_file(wb_obj):
    # - Load cells df

    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    # - Find start times

    time_index_row_nums, start_times = parse_time_headers(df)

    # - Get brynza cleaning time

    if not df[df["label"].str.contains("мойка цеха")].empty:
        m.root.props.update(
            brynza_cleaning_time=df[df["label"].str.contains("мойка цеха")].iloc[0]["x0"] + start_times[-1] - 4 - 1
        )

    # - Parse elements

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

    parse_elements(
        m,
        df,
        "boilings",
        "boiling",
        [time_index_row_nums[0] + i for i in [1, 5, 9, 13]],
        start_times[0],
        length=100,
        split_func=_split_func,
        filter_=_filter_func,
    )

    # parse all blocks at once
    parse_elements(
        m,
        df,
        "blocks",
        "block",
        [time_index_row_nums[0] + i for i in [1, 5, 9, 13]],
        start_times[0],
        length=100,
        split_func=_split_func,
    )

    # - Return

    return m.root


def fill_properties(parsed_schedule):
    props = AdygeaProperties()
    props.is_present = True

    # save boiling_model to parsed_schedule blocks
    boilings = list(sorted(parsed_schedule.iter(cls="boiling"), key=lambda boiling: boiling.y[0]))
    props.n_boilings = len(boilings)
    props.end_time = cast_human_time(boilings[-1].y[0])
    props.brynza_cleaning_time = cast_human_time(parsed_schedule.props["brynza_cleaning_time"])
    return props


def parse_properties(filename):
    parsed_schedule = parse_schedule_file(filename)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        parse_properties(
            str(get_repo_path() / "app/data/static/samples/by_department/adygea/sample_schedule_adygea.xlsx")
        )
    )


if __name__ == "__main__":
    test()
