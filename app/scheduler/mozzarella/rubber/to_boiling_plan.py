import pandas as pd

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import AdygeaSKU, MozzarellaSKU, cast_model
from app.scheduler.adygea.to_boiling_plan._handle_adygea import _handle_adygea
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.update_absolute_batch_id import update_absolute_batch_id


def to_boiling_plan(wb_obj: BoilingPlanLike):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
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
