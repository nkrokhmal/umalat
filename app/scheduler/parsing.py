from utils_ak.block_tree import *

from app.imports.runtime import *


def group_intervals(intervals, max_length=None, interval_func=None, split_func=None):
    if not interval_func:
        interval_func = lambda interval: [interval[0], interval[1]]
    groups = []

    intervals = list(sorted(intervals, key=lambda interval: interval_func(interval)[0]))

    cur_group = []
    for interval in intervals:
        if not cur_group:
            cur_group.append(interval)
            continue

        if interval_func(cur_group[-1])[-1] == interval_func(interval)[0] and not (split_func and split_func(interval)):

            # subsequent
            cur_group.append(interval)
            if max_length and len(cur_group) == max_length:
                groups.append(cur_group)
                cur_group = []
        else:

            # gap between
            groups.append(cur_group)
            cur_group = [interval]

    if cur_group:
        groups.append(cur_group)
    return groups


def test_group_intervals():
    intervals = [[1, 2], [4, 5], [2, 4], [10, 11]]
    intervals = list(sorted(intervals, key=lambda interval: interval[0]))
    assert group_intervals(intervals, max_length=2) == [
        [[1, 2], [2, 4]],
        [[4, 5]],
        [[10, 11]],
    ]


def load_cells_df(wb_obj, sheet_name):
    wb = utils.cast_workbook(wb_obj)

    ws = wb[sheet_name]

    # - Get merged cells

    df = pd.DataFrame()

    df["cell"] = ws.merged_cells.ranges

    bound_names = ("x0", "x1", "y0", "y1")

    df["bounds"] = df["cell"].apply(lambda cell: cell.bounds)
    for i in range(4):
        df[bound_names[i]] = df["bounds"].apply(lambda bound: bound[i])

    df.pop("bounds")

    df["y0"] += 1
    df["y1"] += 1
    df["label"] = df["cell"].apply(lambda cell: cell.start_cell.value)

    df = df.sort_values(by=["x1", "x0", "y1", "y0"])

    df1 = df.copy()

    # - Get non-empty single cells

    non_empty_cells = []
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is not None:
                non_empty_cells.append(cell)

    df = pd.DataFrame()

    df["cell"] = non_empty_cells
    df["label"] = df["cell"].apply(lambda cell: cell.value)
    df["x0"] = df["cell"].apply(lambda cell: cell.col_idx)
    df["y0"] = df["x0"] + 1
    df["x1"] = df["cell"].apply(lambda cell: cell.row)
    df["y1"] = df["x1"] + 1

    df2 = df.copy()

    # - Merge

    df = pd.concat([df1, df2])

    # - Filter duplicates

    df = df.drop_duplicates(subset=["x0", "x1"])

    # - Return

    return df


def test_load_cells_df():
    df = load_cells_df("/Users/arsenijkadaner/Downloads/2023-07-09 Расписание маскарпоне.xlsx", "Расписание")
    print(df)


def parse_block(
    m,
    merged_cells_df,
    label,
    element_label,
    rows,
    start_time,
    length=2,
    split_func=None,
    filter=None,
):
    with m.row(label, x=start_time, push_func=add_push):
        for i, row_num in enumerate(rows):
            df1 = merged_cells_df[
                (merged_cells_df["x1"] == row_num) & (merged_cells_df["x0"] >= 4)
            ]  # filter column header
            groups = group_intervals(
                [row for i, row in df1.iterrows()],
                max_length=length,
                interval_func=lambda row: [row["x0"], row["y0"]],
                split_func=split_func,
            )

            for group in groups:
                if filter and not filter(group):
                    continue

                try:
                    boiling_id = int(group[0]["label"].split(" ")[0])
                except Exception as e:
                    boiling_id = None

                m.row(
                    element_label,
                    size=group[-1]["y0"] - group[0]["x0"],
                    x=group[0]["x0"] - 5,  # subtract column header
                    boiling_id=boiling_id,
                    line_num=str(i),
                    row_num=row_num,
                    group=group,
                    label=str(boiling_id),
                    push_func=add_push,
                )


if __name__ == "__main__":
    test_load_cells_df()
    #
