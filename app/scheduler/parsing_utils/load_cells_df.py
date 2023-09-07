import pandas as pd

from utils_ak.openpyxl import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path


def load_cells_df(wb_obj, sheet_name):
    wb = cast_workbook(wb_obj)

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
    df["label"] = df["cell"].apply(lambda cell: cell.start_cell.value).astype(str)

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
    df["label"] = df["cell"].apply(lambda cell: cell.value).astype(str)
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


def test():
    print(
        load_cells_df(
            str(
                get_repo_path()
                / "app/data/static/samples/by_department/mozzarella/2023-09-04 Расписание моцарелла.xlsx"
            ),
            "Расписание",
        )
    )


if __name__ == "__main__":
    test()
