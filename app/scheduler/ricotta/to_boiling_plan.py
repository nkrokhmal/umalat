import copy
import string

import pandas as pd

from openpyxl import Workbook, load_workbook
from openpyxl.utils.cell import column_index_from_string
from utils_ak.openpyxl import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path


def to_boiling_plan(wb_obj: str | Workbook | pd.DataFrame, saturate=True, first_batch_ids_by_type={"ricotta": 1}):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """

    # - If already a dataframe, return it

    if isinstance(wb_obj, pd.DataFrame):
        # already a dataframe
        return wb_obj

    # - Read sheet
    wb = cast_workbook(wb_obj)
    ws = wb["План варок"]

    # - Collect values from sheet

    # -- Init values

    values = []

    # -- collect header

    header_and_indexes = [(ws.cell(1, i).value, i) for i in range(1, 100) if ws.cell(1, i).value]
    # -- Collect values

    for j in range(2, 200):
        if not ws.cell(j, 2).value:
            continue

        values.append([ws.cell(j, header_and_index[1]).value for header_and_index in header_and_indexes])

    df = pd.DataFrame(values, columns=[header_and_index[0] for header_and_index in header_and_indexes])
    df = df.fillna(method="bfill")

    df = df[["Номер группы варок", "SKU", "КГ", "Количество варок"]]
    df.columns = ["boiling_group_id", "sku", "kg", "n_boilings"]
    df = df[df["sku"] != "-"]
    df["boiling_group_id"] = df["boiling_group_id"].astype(int)
    df["n_boilings"] = df["n_boilings"].astype(int)

    # - Split boiling groups to boilings

    values = []

    for idx, boiling_group_grp in df.groupby("boiling_group_id"):
        group_records = boiling_group_grp.to_dict(orient="records")
        for i in range(boiling_group_grp.iloc[0]["n_boilings"]):
            # - Copy cur_values

            current_group_records = copy.deepcopy(group_records)

            # - Update boiling_group_id

            for group_record in current_group_records:
                group_record["boiling_id"] = f"{idx}-{i + 1}"

            # - Add group to values

            values += current_group_records

    df = pd.DataFrame(values)

    return df


def test():
    df = to_boiling_plan(str(get_repo_path() / "app/data/tests/ricotta/boiling.xlsx"))
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)

    print(df)


if __name__ == "__main__":
    test()
