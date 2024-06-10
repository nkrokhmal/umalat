import pandas as pd

from loguru import logger
from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import BrynzaSKU, cast_model
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.calc_absolute_batch_id import calc_absolute_batch_id


def to_boiling_plan(
    wb_obj: BoilingPlanLike,
    first_batch_ids_by_type={"brynza": 1},
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

    # - Check if already a dataframe

    if isinstance(wb_obj, pd.DataFrame):

        # already a dataframe
        return wb_obj

    # - Cast to workbook

    wb = cast_workbook(wb_obj)

    # - Load worksheet

    ws = None
    for key in ["План варок", "План варок брынза"]:
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

    # - Post-process data

    # -- Basic

    df = df[["Номер группы варок", "SKU", "КГ"]]
    df.columns = [
        "group_id",
        "sku",
        "kg",
    ]
    df = df[df["sku"] != "-"]

    if df.empty:
        logger.info("Empty data frame")
        df = pd.DataFrame(columns=["boiling_id", "sku", "kg", "boiling"])
    else:
        df["boiling_id"] = df["group_id"]
        df["sku"] = df["sku"].apply(lambda sku: cast_model(BrynzaSKU, sku))
        df["boiling"] = df["sku"].apply(lambda x: x.made_from_boilings[0])

        df = df[["boiling_id", "sku", "kg", "boiling"]]

    # -- Batches

    df["batch_id"] = df["boiling_id"]  # batch_id is the same as boiling_id for brynza
    df["batch_type"] = "brynza"
    df["absolute_batch_id"] = calc_absolute_batch_id(
        boiling_plan_df=df,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )

    # - Return

    return df


def test():
    df = to_boiling_plan(
        str(
            get_repo_path()
            / "app/data/static/samples/by_department/milk_project/2023-11-19 План по варкам милкпроджект Новый.xlsx"
        )
    )
    print(df.iloc[0])
    print("-" * 120)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    print(df)


if __name__ == "__main__":
    test()
