from app.imports.runtime import *
from app.scheduler.time import *
from app.scheduler.parsing_new import *

COLUMN_SHIFT = 5  # header 4 + 1 for one-indexing


def parse_schedule(ws_obj):

    # - Read cells

    df = utils.read_merged_cells_df(ws_obj, basic_features=False)

    # - Find time

    # find time index rows
    time_index_rows = df[df["label"].astype(str).str.contains("График")]["x1"].unique()
    row = time_index_rows[0]

    # extract time
    start_time = cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row)].iloc[0]["label"])

    # - Precaution for minimum start time

    minimum_start_time = "21:00"
    start_time = (
        start_time if cast_t(start_time) <= cast_t(minimum_start_time) else cast_time(cast_t(start_time) - 24 * 12)
    )

    # - Find cheese makers rows

    df1 = df[df["x0"] >= 5]  # column header out

    # find cheese_maker_rows
    rows = []
    for row_num in df1["x1"].unique():
        row_labels = [str(row["label"]) for i, row in df1[df1["x1"] == row_num].iterrows()]
        row_labels = [re.sub(r"\s+", " ", label) for label in row_labels if label]

        if {"налив/внесение закваски", "схватка"}.issubset(set(row_labels)):
            rows.append(row_num - 1)

    # - Iterate over rows and parse boilings

    parsed_schedule = {"boilings": []}

    for i, row in enumerate(rows):

        # - Fine line blocks

        def _filter_func(group):
            try:
                return utils.is_int_like(group.iloc[0]["label"].split(" ")[0])
            except:
                return False

        def _split_func(prev_row, row):
            try:
                return utils.is_int_like(row["label"].split(" ")[0])
            except:
                return False

        line_blocks = parse_line(df, row, split_criteria=basic_criteria(max_length=2, split_func=_split_func))
        line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]

        # - Expand blocks

        def expand_block(df, df_block):
            return df[
                (df["x1"].isin([df_block["x1"].min(), df_block["x1"].min() + 1]))
                & (df_block["x0"].min() <= df["x0"])
                & (df["x0"] < df_block["y0"].max())
            ]

        boiling_dfs = [expand_block(df, line_block) for line_block in line_blocks]

        # - Convert boilings to dictionaries

        for boiling_df in boiling_dfs:
            boiling = boiling_df.set_index("label").to_dict(orient="index")
            boiling = {
                "blocks": {
                    k: [v["x0"] + cast_t(start_time) - COLUMN_SHIFT, v["y0"] + cast_t(start_time) - COLUMN_SHIFT]
                    for k, v in boiling.items()
                },
                "boiling_id": int(boiling_df.iloc[0]["label"].split(" ")[0]),
                "interval": [
                    boiling_df["x0"].min() + cast_t(start_time) - COLUMN_SHIFT,
                    boiling_df["y0"].max() + cast_t(start_time) - COLUMN_SHIFT,
                ],
            }

            boiling["interval_time"] = list(map(cast_human_time, boiling["interval"]))
            boiling["line"] = i + 1

            parsed_schedule["boilings"].append(boiling)

    return parsed_schedule


def test():
    print(
        parse_schedule(
            (
                r"/Users/arsenijkadaner/FileApps/coding_projects/umalat/app/data/static/samples/outputs/by_department/mozzarella/2023-06-21 Расписание моцарелла.xlsx",
                "Расписание",
            )
        )
    )


if __name__ == "__main__":
    test()
