import pandas as pd

from loguru import logger
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.models import AdygeaSKU, cast_model
from app.scheduler.boiling_plan import update_absolute_batch_id
from app.utils.features.merge_boiling_utils import Boilings


def read_boiling_plan(wb_obj, first_batch_ids=None):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    first_batch_ids = first_batch_ids or {"adygea": 1}
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

    df_plan, boiling_number = handle_adygea(df)  # convert to boiligns

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
    df_plan = update_absolute_batch_id(df_plan, first_batch_ids)
    return df_plan


def proceed_order(df_filter, boilings_adygea, boilings_count=1):
    if not df_filter.empty:
        boilings_adygea.init_iterator(df_filter["output"].iloc[0])
        boilings_adygea.add_group(
            df_filter.to_dict("records"),
            boilings_count=boilings_count,
        )
    return boilings_adygea


def handle_adygea(df):
    df["sku"] = df["sku"].apply(lambda sku: cast_model(AdygeaSKU, sku))
    df["plan"] = df["kg"]
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)

    boilings_adygea = Boilings()
    for i, df_filter in df.groupby("group_id"):
        boilings_adygea = proceed_order(df_filter, boilings_adygea)
    boilings_adygea.finish()
    return pd.DataFrame(boilings_adygea.boilings), boilings_adygea.boiling_number
