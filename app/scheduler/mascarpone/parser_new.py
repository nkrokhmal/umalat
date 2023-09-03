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
from app.scheduler.time_utils import cast_human_time, cast_t, cast_time


COLUMN_SHIFT = 5  # header 4 + 1 for one-indexing


def parse_schedule(ws_obj):
    df = read_merged_cells_df(ws_obj, basic_features=False)

    with code("Find time"):
        # find time index rows
        time_index_rows = df[df["label"].astype(str).str.contains("График")]["x1"].unique()
        row = time_index_rows[0]

        # extract time
        start_time = cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row)].iloc[0]["label"])

        with code("Precaution for minimum start time"):
            minimum_start_time = "21:00"
            start_time = (
                start_time
                if cast_t(start_time) <= cast_t(minimum_start_time)
                else cast_time(cast_t(start_time) - 24 * 12)
            )

    with code("find rows"):
        df1 = df[df["x0"] >= 5]  # column header out

        mascarpone_rows = []
        cream_cheese_rows = []

        # find cheese_maker_rows
        for row_num in df1["x1"].unique():
            row_labels = [str(row["label"]) for i, row in df1[df1["x1"] == row_num].iterrows()]
            row_labels = [re.sub(r"\s+", " ", label) for label in row_labels if label]

            if any("производство" in row_label for row_label in row_labels):
                mascarpone_rows.append(row_num)

            if "охлаждение" in row_labels:
                cream_cheese_rows.append(row_num)

    # leave only bath lines (3 items)
    parsed_schedule = {"mascarpone_boilings": [], "cream_cheese_boilings": []}
    with code("mascarpone boilings"):
        for i, row in enumerate(mascarpone_rows):
            with code("find line blocks for mascarpone"):

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

                line_blocks = parse_line(df, row, split_criteria=basic_criteria(max_length=2, split_func=_split_func))
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
                    boiling_df["is_cream"] = boiling_df["label"].apply(lambda s: "сливок" in s)
                    boiling_df["id"] = boiling_df.apply(lambda row: row["label"] + "-" + str(row["color"]), axis=1)
                    boiling = boiling_df.set_index("id").to_dict(orient="index")
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
                    boiling["line"] = i + 1
                    boiling["type"] = "cream" if boiling_df["is_cream"].any() else "mascarpone"
                    parsed_schedule["mascarpone_boilings"].append(boiling)
    with code("cream cheese boilings"):
        for i, row in enumerate(cream_cheese_rows):
            with code("find line blocks for mascarpone"):

                def _filter_func(group):
                    try:
                        return group.iloc[0]["label"] == "охлаждение"
                    except:
                        return False

                def _split_func(prev_row, row):
                    try:
                        return is_int_like(row["label"].split(" ")[0]) or "охлаждение" in row["label"]
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
                    boiling_df["id"] = boiling_df.apply(lambda row: row["label"] + "-" + str(row["color"]), axis=1)
                    boiling_df = boiling_df.drop_duplicates(
                        subset="id", keep="last"
                    )  # NOTE: LOSE SOME INFORMATION (since we all duplicates block from the start), unnesecary for this point. If needed duplicated blocks - another solution needed
                    boiling = boiling_df.set_index("id").to_dict(orient="index")
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
                    boiling["type"] = "cream_cheese"
                    parsed_schedule["cream_cheese_boilings"].append(boiling)

    # calc boilings
    df = pd.DataFrame(parsed_schedule["mascarpone_boilings"])

    if len(df) > 0:
        parsed_schedule["mascarpone_boiling_groups"] = []
        for (boiling_type, boiling_id), grp in df.groupby(["type", "boiling_id"]):
            boiling = {"boiling_id": boiling_id}
            boiling["interval"] = [
                min(grp["interval"].apply(lambda interval: interval[0])),
                max(grp["interval"].apply(lambda interval: interval[1])),
            ]
            boiling["interval_time"] = list(map(cast_human_time, boiling["interval"]))
            boiling["type"] = grp.iloc[0]["type"]
            parsed_schedule["mascarpone_boiling_groups"].append(boiling)
    return parsed_schedule


def test():
    fn = os.path.join(basedir, "app/data/static/samples/outputs/by_department/mascarpone/Расписание маскарпоне 8.xlsx")
    df = pd.DataFrame(parse_schedule((fn, "Расписание"))["mascarpone_boiling_groups"])
    # df = pd.DataFrame(parse_schedule((fn, 'Расписание'))['cream_cheese_boilings'])
    # print(df[['type', 'interval_time']])
    print(df)


if __name__ == "__main__":
    test()
