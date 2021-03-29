from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.schedule_maker.departments.ricotta.boiling_plan.saturate import (
    saturate_boiling_plan,
)
from openpyxl.utils.cell import column_index_from_string
from copy import copy


INDEX_COLUMN = column_index_from_string("A")
NAME_COLUMN = column_index_from_string("E")
COUNT_COLUMN = column_index_from_string("Q")



def read_boiling_plan(wb_obj, saturate=True):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

    ws_name = "План варок"
    ws = wb[ws_name]
    values = []

    # collect header
    header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

    current_boiling = []
    index_offset = 0
    for i in range(2, 200):
        if not ws.cell(i, 2).value:
            continue
        if ws.cell(i, NAME_COLUMN).value == '-':
            if isinstance(ws.cell(i, COUNT_COLUMN).value, int):
                for j in range(ws.cell(i, COUNT_COLUMN).value):
                    current_boiling_df = pd.DataFrame(current_boiling)
                    current_boiling_df[INDEX_COLUMN - 1] += index_offset + j
                    values += current_boiling_df.values.tolist()
                current_boiling = []
                index_offset += ws.cell(i, COUNT_COLUMN).value - 1
            else:
                raise AssertionError(
                    "В одной из варок не указано количество варок"
                )
        else:
            current_boiling.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])
        # values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])
    df = pd.DataFrame(values, columns=header)
    df = df[["Номер группы варок", "SKU", "КГ", "Выход с варки, кг", "Количество варок"]]
    df.columns = ["boiling_id", "sku", "kg", "output", "count"]

    # remove separators and empty lines
    df = df[df["sku"] != "-"]
    df = df[~df["kg"].isnull()]

    df["sku"] = df["sku"].apply(lambda sku: cast_model(RicottaSKU, sku))
    df["boiling"] = df["sku"].apply(lambda sku: sku.made_from_boilings[0])
    df["boiling_id"] = df["boiling_id"].astype(int)

    for idx, grp in df.groupby("boiling_id"):
        assert (
            len(grp["boiling"].unique()) == 1
        ), "В одной варке должен быть только один тип варки"

        assert (
            len(grp["output"].unique()) == 1
        ), "В одной варке должны совпадать выходы с варки"

        # fix number of kilograms
        if abs(grp["kg"].sum() - grp.iloc[0]["output"]) / grp.iloc[0]["output"] > 0.05:
            raise AssertionError(
                "Одна из групп варок имеет неверное количество килограмм."
            )
        else:
            if abs(grp["kg"].sum() - grp.iloc[0]["output"]) > 1e-5:
                df.loc[grp.index, "kg"] *= (
                    grp.iloc[0]["output"] / grp["kg"].sum()
                )  # scale to total_volume
            else:
                # all fine
                pass
    if saturate:
        df = saturate_boiling_plan(df)
    return df
