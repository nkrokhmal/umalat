import pandas as pd

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import AdygeaSKU, cast_model
from app.scheduler.adygea.to_boiling_plan._handle_adygea import _handle_adygea
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.update_absolute_batch_id import update_absolute_batch_id


def to_boiling_plan(wb_obj: BoilingPlanLike, first_batch_ids_by_type={"adygea": 1}):
    """Считать файл плана варок в датафрейм

    Может читать и файл расписания, т.к. там там обычно есть лист с планом варок

    :param boiling_plan_source: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg', ...])
    """

    if isinstance(wb_obj, pd.DataFrame):
        # already a dataframe
        return wb_obj

    wb = cast_workbook(wb_obj)

    cur_id = 0

    with code("Load boiling plan"):
        ws = None
        for key in ["План варок", "План варок адыгейский"]:
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
    df = df[["Номер группы варок", "SKU", "КГ"]]
    df.columns = [
        "group_id",
        "sku",
        "kg",
    ]
    df = df[df["sku"] != "-"]

    df_plan, boiling_number = _handle_adygea(df)  # convert to boiligns

    if df_plan.empty:
        logger.info("Empty data frame")
        df_plan = pd.DataFrame(columns=["boiling_id", "sku", "n_baths", "kg", "boiling"])
    else:
        df_plan["boiling_id"] = df_plan["id"]
        df_plan["kg"] = df_plan["plan"]
        df_plan["n_baths"] = 1  # todo maybe: redundant
        df_plan["boiling_id"] = df_plan["boiling_id"].astype(int) + 1
        df_plan["sku"] = df_plan["sku"].apply(lambda sku: cast_model(AdygeaSKU, sku.name))
        df_plan["boiling"] = df_plan["sku"].apply(lambda x: x.made_from_boilings[0])

        df_plan = df_plan[["boiling_id", "sku", "n_baths", "kg", "boiling"]]

    # batch_id and boiling_id are the same
    df_plan["batch_id"] = df_plan["boiling_id"]
    df_plan["batch_type"] = "adygea"
    df_plan = update_absolute_batch_id(df_plan, first_batch_ids_by_type)
    return df_plan


def test():
    df = to_boiling_plan(
        str(
            get_repo_path() / "app/data/static/samples/by_department/adygea/2023-09-03 План по варкам милкпроджект.xlsx"
        )
    )
    print(df.iloc[0])


if __name__ == "__main__":
    test()
