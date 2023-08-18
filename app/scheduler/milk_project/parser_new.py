import os
import re

import numpy as np
import pandas as pd

from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.types import is_int_like
from utils_ak.openpyxl.openpyxl_tools import read_merged_cells_df

from app.globals import basedir
from app.scheduler.parsing_new.group_intervals import basic_criteria
from app.scheduler.parsing_new.parse_time import cast_time_from_hour_label
from app.scheduler.parsing_new.parsing import parse_line
from app.scheduler.time import cast_human_time, cast_t


COLUMN_SHIFT = 5  # header 4 + 1 for one-indexing


def parse_schedule(ws_obj):
    df = read_merged_cells_df(ws_obj, basic_features=False)

    with code("Find times"):
        # find time index rows
        time_index_rows = df[df["label"].astype(str).str.contains("График")]["x1"].unique()
        row = time_index_rows[0]

        start_time = cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row)].iloc[0]["label"])

    with code("find rows"):
        df1 = df[df["x0"] >= 5]  # column header out

        adygea_rows = []
        milk_project_rows = []
        for row_num in df1["x1"].unique():
            row_labels = [str(row["label"]) for i, row in df1[df1["x1"] == row_num].iterrows()]
            row_labels = [re.sub(r"\s+", " ", label) for label in row_labels if label]

            if "Набор смеси" in row_labels:
                milk_project_rows.append(row_num)

            with code("find all adygea rows "):
                _labels = [label.replace("налив", "") for label in row_labels]
                _labels = [re.sub(r"\s+", "", label) for label in _labels]
                int_labels = [int(label) for label in _labels if is_int_like(label)]

                if not ("05" in row_labels and "55" in row_labels):
                    # not a time header
                    if int_labels:
                        adygea_rows.append(row_num)

    parsed_schedule = {"milk_project_boilings": [], "adygea_boilings": []}

    with code("milk project"):
        for i, row in enumerate(milk_project_rows):
            with code("find line blocks"):

                def _filter_func(group):
                    try:
                        return "набор смеси" in group.iloc[0]["label"].lower()
                    except:
                        return False

                def _split_func(prev_row, row):
                    try:
                        return "набор смеси" in row["label"].lower()
                    except:
                        return False

                line_blocks = parse_line(df, row, split_criteria=basic_criteria(split_func=_split_func))
                line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]

            boiling_dfs = line_blocks

            with code("Convert boilings to dictionaries"):
                for boiling_df in boiling_dfs:
                    boiling_df["label"] = np.where(
                        boiling_df["label"].isnull(), boiling_df["color"], boiling_df["label"]
                    )
                    boiling = boiling_df.set_index("label").to_dict(orient="index")
                    boiling = {
                        "blocks": {
                            k: [
                                v["x0"] + cast_t(start_time) - COLUMN_SHIFT,
                                v["y0"] + cast_t(start_time) - COLUMN_SHIFT,
                            ]
                            for k, v in boiling.items()
                        }
                    }

                    boiling["boiling_id"] = None
                    boiling["interval"] = [
                        boiling_df["x0"].min() + cast_t(start_time) - COLUMN_SHIFT,
                        boiling_df["y0"].max() + cast_t(start_time) - COLUMN_SHIFT,
                    ]
                    boiling["interval_time"] = list(map(cast_human_time, boiling["interval"]))

                    parsed_schedule["milk_project_boilings"].append(boiling)

    with code("adygea"):
        for i, row in enumerate(adygea_rows):
            with code("find line blocks"):

                def _filter_func(group):
                    try:
                        return is_int_like(group.iloc[0]["label"].split(" ")[0])
                    except:
                        return False

                def _split_func(prev_row, row):
                    try:
                        return is_int_like(row["label"].split(" ")[0])
                    except:
                        return False

                line_blocks = parse_line(df, row, split_criteria=basic_criteria(split_func=_split_func))
                line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]

            with code("expand blocks"):

                def expand_block(df, df_block):
                    return df[
                        (df["x1"].isin([df_block["x1"].min(), df_block["x1"].min() + 1]))
                        & (df_block["x0"].min() <= df["x0"])
                        & (df["x0"] < df_block["y0"].max())
                    ]

                boiling_dfs = [expand_block(df, line_block) for line_block in line_blocks]

            with code("Convert boilings to dictionaries"):
                for boiling_df in boiling_dfs:
                    boiling_df["label"] = np.where(
                        boiling_df["label"].isnull() | (boiling_df["label"] == ""),
                        boiling_df["color"],
                        boiling_df["label"],
                    )
                    boiling = boiling_df.set_index("label").to_dict(orient="index")
                    boiling = {
                        "blocks": {
                            k: [
                                v["x0"] + cast_t(start_time) - COLUMN_SHIFT,
                                v["y0"] + cast_t(start_time) - COLUMN_SHIFT,
                            ]
                            for k, v in boiling.items()
                        }
                    }
                    boiling["boiling_id"] = int(boiling_df.iloc[0]["label"].split(" ")[0])
                    boiling["interval"] = [
                        boiling_df["x0"].min() + cast_t(start_time) - COLUMN_SHIFT,
                        boiling_df["y0"].max() + cast_t(start_time) - COLUMN_SHIFT,
                    ]
                    boiling["interval_time"] = list(map(cast_human_time, boiling["interval"]))

                    parsed_schedule["adygea_boilings"].append(boiling)

    return parsed_schedule


def test():
    fn = os.path.join(
        basedir,
        "app/data/static/samples/outputs/by_department/milk_project/Расписание милкпроджект 3 несколько милок.xlsx",
    )
    df = pd.DataFrame(parse_schedule((fn, "Расписание"))["milk_project_boilings"])[["boiling_id", "interval_time"]]
    print(df)


if __name__ == "__main__":
    test()
