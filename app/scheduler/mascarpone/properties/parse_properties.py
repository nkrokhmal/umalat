import pandas as pd

from utils_ak.block_tree.block_maker import BlockMaker

from app.scheduler.common.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.common.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.common.parsing_utils.parse_block import parse_elements
from app.scheduler.common.parsing_utils.parse_time_headers import parse_time_headers
from app.scheduler.common.time_utils import cast_human_time, cast_t
from app.scheduler.mascarpone.properties.mascarpone_properties import MascarponeProperties


def parse_schedule_file(wb_obj):
    # - Load cells

    df = load_cells_df(wb_obj, "Расписание")

    # - Init block maker

    m = BlockMaker("root")

    # - Find separation for mascarpone

    values = []
    for i, row in df.loc[df["label"].str.contains("Производство маскарпоне")].iterrows():
        # - Find all separation blocks in +2 row that are within the same column range

        _separation_blocks_df = df[
            df["label"].str.contains("Сепарирование")
            & (df["x0"] >= row["x0"])
            & (df["x0"] <= row["y0"] + 1)
            & (df["x1"] == row["x1"] + 2)
        ]
        _separation_blocks_df["kg"] = _separation_blocks_df["label"].apply(
            lambda s: int(s.split(" ")[-1].replace("кг", "")) if "кг" in s else 0
        )
        values += _separation_blocks_df.to_dict(orient="records")
    if values:
        separation_blocks_df = pd.DataFrame(values).sort_values(by="x0")
        m.root.props.update(separation_blocks_df=separation_blocks_df)

    # - Parse rows to schedule

    # -- Find start times

    time_index_row_nums, start_times = parse_time_headers(cells_df=df)

    # - Parse rows to schedule

    for i, row_num in enumerate(time_index_row_nums):
        parse_elements(
            m,
            df,
            "last_rows",
            "last_row",
            [time_index_row_nums[i] + 9],
            start_times[i],
            length=100,
        )

    return m.root


def fill_properties(parsed_schedule):
    # - Init properties

    props = MascarponeProperties()
    props.is_present = True

    # - Fill end time

    props.end_time = cast_human_time(parsed_schedule.y[0])

    # - Fill every_8t_of_separation

    separation_blocks_df = parsed_schedule.props["separation_blocks_df"]

    props.every_8t_of_separation = []

    if separation_blocks_df is not None:
        separation_blocks_df["kg_cumsum"] = separation_blocks_df["kg"].cumsum()

        current_kg = 0
        for i, row in separation_blocks_df.iterrows():
            current_kg += row["kg"]
            if current_kg >= 8000:
                props.every_8t_of_separation.append(cast_human_time(row["y0"]))
                break
        props.every_8t_of_separation.append(cast_human_time(separation_blocks_df.iloc[-1]["y0"]))  # max 2 times
        props.every_8t_of_separation = list(sorted(set(props.every_8t_of_separation)))

    return props


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    props = fill_properties(parsed_schedule)
    return props


def test():
    print(
        pd.DataFrame(
            parse_properties(
                """/Users/marklidenberg/Desktop/2024.04.06 contour_cleanings/2024-03-02/approved/2024-03-02 Расписание моцарелла.xlsx"""
            )
        )
    )


if __name__ == "__main__":
    test()
