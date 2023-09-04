import os

import pandas as pd

from utils_ak.openpyxl.openpyxl_tools import read_merged_cells_df

from lessmore.utils.get_repo_path import get_repo_path

from app.globals import basedir
from app.scheduler.parsing_new_utils.group_intervals import basic_criteria
from app.scheduler.parsing_new_utils.parse_time import cast_time_from_hour_label
from app.scheduler.parsing_new_utils.parsing import parse_line
from app.scheduler.time_utils import cast_human_time, cast_t


COLUMN_SHIFT = 5  # header 4 + 1 for one-indexing


def parse_schedule(ws_obj):
    # - Get cells from worksheet object

    df = read_merged_cells_df(ws_obj, basic_features=False)

    # - Find time

    # find time index rows
    time_index_rows = df[df["label"].astype(str).str.contains("График")]["x1"].unique()
    row = time_index_rows[0]

    # extract time
    start_time = cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row)].iloc[0]["label"])

    # _ Find line block
    parsed_schedule = {"boilings": []}

    def _filter_func(group):
        try:
            return "анализы" in group.iloc[0]["label"]
        except:
            return False

    def _split_func(prev_row, row):
        try:
            return "анализы" in row["label"].lower() or "фасовка" in row["label"].lower()
        except:
            return False

    line_blocks = parse_line(df, 2, split_criteria=basic_criteria(split_func=_split_func))
    line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]
    boiling_dfs = line_blocks

    # - Convert boilings to dictionaries

    for boiling_df in boiling_dfs:
        boiling = boiling_df.set_index("label").to_dict(orient="index")
        boiling = {
            "blocks": {
                k: [v["x0"] + cast_t(start_time) - COLUMN_SHIFT, v["y0"] + cast_t(start_time) - COLUMN_SHIFT]
                for k, v in boiling.items()
            }
        }

        boiling["boiling_id"] = None

        boiling["interval"] = [
            boiling_df["x0"].min() + cast_t(start_time) - COLUMN_SHIFT,
            boiling_df["y0"].max() + cast_t(start_time) - COLUMN_SHIFT,
        ]
        boiling["interval_time"] = list(map(cast_human_time, boiling["interval"]))
        parsed_schedule["boilings"].append(boiling)

    # - Return parsed schedule

    return parsed_schedule


def test():
    print(
        pd.DataFrame(
            parse_schedule(
                (
                    str(
                        get_repo_path()
                        / "app/data/static/samples/by_department/butter/2023-09-03 План по варкам масло.xlsx"
                    ),
                    "Расписание",
                )
            )
        )
    )


if __name__ == "__main__":
    test()
