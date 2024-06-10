import pandas as pd

from loguru import logger
from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import AdygeaSKU, cast_model
from app.scheduler.adygea.to_boiling_plan._split_by_boilings import _split_by_boilings
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.calc_absolute_batch_id import calc_absolute_batch_id


def to_boiling_plan(
    wb_obj: BoilingPlanLike,
    first_batch_ids_by_type: dict = {"adygea": 1},
):
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

    # - Load worksheet

    ws = None
    for key in ["План варок", "План варок адыгейский"]:
        if key in wb.sheetnames:
            ws = wb[key]
    if not ws:
        raise Exception("Не найдена вкладка для плана варок")

    # - Read data

    values = []

    # collect header
    header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

    for i in range(2, 200):
        if not ws.cell(i, 2).value:
            continue

        values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

    df = pd.DataFrame(values, columns=header)

    # - Post processing

    # -- Basic

    df = df[["Номер группы варок", "SKU", "КГ"]]
    df.columns = [
        "group_id",
        "sku",
        "kg",
    ]
    df = df[df["sku"] != "-"]

    df["sku"] = df["sku"].apply(lambda sku: cast_model(AdygeaSKU, sku))
    df["plan"] = df["kg"]
    df["output"] = df["sku"].apply(lambda x: x.made_from_boilings[0].output_kg)

    # -- Split by boilings

    df = _split_by_boilings(df)

    # -- Post processing for splitted dataframe

    if df.empty:
        logger.info("Empty data frame")
        df = pd.DataFrame(columns=["boiling_id", "sku", "kg", "boiling"])
    else:
        df["boiling_id"] = df["id"]
        df["kg"] = df["plan"]
        df["boiling_id"] = df["boiling_id"].astype(int) + 1
        df["sku"] = df["sku"].apply(lambda sku: cast_model(AdygeaSKU, sku.name))
        df["boiling"] = df["sku"].apply(lambda x: x.made_from_boilings[0])

        df = df[["boiling_id", "sku", "kg", "boiling"]]

    # -- Batches

    df["batch_id"] = df["boiling_id"]  # batch id is the same as boiling id for adygea
    df["batch_type"] = "adygea"
    df["absolute_batch_id"] = calc_absolute_batch_id(df, first_batch_ids_by_type)
    return df


def test():
    df = to_boiling_plan(
        str(get_repo_path() / "app/data/static/samples/by_department/adygea/sample_schedule_adygea.xlsx"),
    )
    print(df.iloc[0])

    print("-" * 88)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    print(df)


if __name__ == "__main__":
    test()
