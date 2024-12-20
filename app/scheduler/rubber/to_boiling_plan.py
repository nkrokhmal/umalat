import numpy as np
import pandas as pd

from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import MozzarellaSKU, cast_model
from app.scheduler.common.boiling_plan_like import BoilingPlanLike

def split_rubber_boiling_plan(df: pd.DataFrame):
    result = []
    for _, row in df.iterrows():
        packing_speed = row["sku"].packing_speed
        kg = row["kg"]
        n = kg // packing_speed
        kgs = [packing_speed * 1] * n + [kg - packing_speed * n * 1]
        result += [[row["sku"], kg] for kg in kgs if kg > 0]

    df = pd.DataFrame(result, columns=["sku", "kg"])
    df["sku_name"] = df["sku"].apply(lambda x: x.name)
    df["original_kg"] = df["kg"]
    df["line"] = df["sku"].apply(lambda x: x.line)
    df["absolute_batch_id"] = np.arange(len(df)) + 1
    return df


def to_boiling_plan(wb_obj: BoilingPlanLike):
    """Считать файл плана варок в датафрейм

    Может читать и файл расписания, т.к. там там обычно есть лист с планом варок

    Parameters
    ----------
    boiling_plan_source : str or openpyxl.Workbook or pd.DataFrame
        Путь к файлу плана варок или сам файл

    Returns
    -------
    pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg', ...])
    """

    if isinstance(wb_obj, pd.DataFrame):

        # already a dataframe
        return wb_obj

    wb = cast_workbook(wb_obj)

    cur_id = 0

    # - Get worksheet

    ws = None
    for key in ["Терка"]:
        if key in wb.sheetnames:
            ws = wb[key]
    if not ws:
        raise Exception("Не найдена вкладка для плана варок")

    values = []

    # collect header
    header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

    for i in range(2, 200):
        if not ws.cell(i, 2).value:
            continue

        values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

    df = pd.DataFrame(values, columns=header)
    df = df[["SKU", "КГ"]]
    df.columns = ["sku", "kg"]

    df["sku"] = df["sku"].apply(lambda sku: cast_model(MozzarellaSKU, sku))
    df = df[df["kg"] > 0]
    return df


def test():
    df = to_boiling_plan(
        str(get_repo_path() / "app/data/static/samples/by_department/rubber/sample_rubber_schedule.xlsx")
    )
    print(df.iloc[0])

    print("-" * 88)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    print(df)


if __name__ == "__main__":
    test()
