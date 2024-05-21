import pandas as pd

from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.models import AdygeaSKU, MozzarellaSKU, cast_model
from app.scheduler.boiling_plan_like import BoilingPlanLike


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
        """/Users/marklidenberg/Desktop/2024.04.19 терка мультиголовы/2024-03-08 План по варкам моцарелла.xlsx"""
    )
    print(df.iloc[0])


if __name__ == "__main__":
    test()
