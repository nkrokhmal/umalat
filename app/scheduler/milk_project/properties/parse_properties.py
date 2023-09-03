from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.milk_project.properties.milk_project_properties import MilkProjectProperties
from app.scheduler.parsing_new.parse_time import cast_time_from_hour_label
from app.scheduler.parsing_utils import load_cells_df, parse_block
from app.scheduler.time_utils import cast_human_time, cast_t


def parse_schedule_file(wb_obj):
    df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    with code("Find split rows"):
        df1 = df[df["label"] == "Набор смеси"]
        split_rows = df1["x1"].unique()

    with code("Find start times"):
        time_index_row_nums = df[df["label"].astype(str).str.contains("График")]["x1"].unique()

        start_times = []

        for row_num in time_index_row_nums:
            start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))

        # todo maybe: refactor start_times -> start_ts [@marklidenberg]
        start_times = [cast_t(v) for v in start_times]

    def _split_func(row):
        try:
            return row["label"].split(" ")[0] == "Набор воды в машину"
        except:
            return False

    parse_block(
        m, df, "boilings", "boiling", [i for i in split_rows], start_times[0], length=100, split_func=_split_func
    )

    return m.root


def fill_properties(parsed_schedule):
    props = MilkProjectProperties()

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
                    / "app/data/static/samples/outputs/by_department/milk_project/Расписание милк проджект 1 без милки.xlsx"
                )
            )
        )
    )


if __name__ == "__main__":
    test()
