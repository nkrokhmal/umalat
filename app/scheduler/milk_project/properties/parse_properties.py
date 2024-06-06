from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.common.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.common.parsing_utils.parse_block import parse_elements
from app.scheduler.common.parsing_utils.parse_time_headers import parse_time_headers
from app.scheduler.common.time_utils import cast_human_time, cast_t
from app.scheduler.milk_project.properties.milk_project_properties import MilkProjectProperties


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    # - Find split rows

    df1 = df[df["label"] == "Набор смеси"]
    split_rows = df1["x1"].unique()

    # - Find start times

    time_index_row_nums, start_times = parse_time_headers(cells_df=df)

    # - Parse boilings

    def _split_func(row):
        try:
            return row["label"].split(" ")[0] == "Набор воды в машину"
        except:
            return False

    parse_elements(
        m, df, "boilings", "boiling", [i for i in split_rows], start_times[0], length=100, split_func=_split_func
    )

    return m.root


def fill_properties(parsed_schedule):
    props = MilkProjectProperties()
    props.is_present = True

    # save boiling_model to parsed_schedule blocks
    boilings = list(sorted(parsed_schedule.iter(cls="boiling"), key=lambda boiling: boiling.y[0]))
    if boilings:
        props.n_boilings = len(boilings)
        props.end_time = cast_human_time(boilings[-1].y[0])
    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        dict(
            parse_properties(
                str(
                    get_repo_path()
                    / "app/data/static/samples/by_department/milk_project/Расписание милкпроджект 3 несколько милок.xlsx"
                )
            )
        )
    )


if __name__ == "__main__":
    test()
