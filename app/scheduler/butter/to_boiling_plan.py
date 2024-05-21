import pandas as pd

from utils_ak.builtin import delistify
from utils_ak.openpyxl.openpyxl_tools import cast_workbook

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import ButterSKU, cast_model
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.calc_absolute_batch_id import calc_absolute_batch_id


def to_boiling_plan(
    boiling_plan_source: BoilingPlanLike,
    first_batch_ids_by_type: dict = {"butter": 1},
) -> pd.DataFrame:
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

    if isinstance(boiling_plan_source, pd.DataFrame):
        # already a dataframe
        return boiling_plan_source

    # - Read boiling plan

    wb = cast_workbook(boiling_plan_source)

    ws = wb["План варок"]

    values = []

    # collect header
    header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

    for i in range(2, 200):
        if not ws.cell(i, 2).value:
            continue

        values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

    df = pd.DataFrame(values, columns=header)

    # - Post-process dataframe

    # -- Basic

    df = df[["Номер группы варок", "SKU", "КГ"]]
    df.columns = ["group_id", "sku", "kg"]
    df = df[df["sku"] != "-"]
    df["group_id"] = df["group_id"].astype(int)
    df["sku"] = df["sku"].apply(lambda sku: cast_model(ButterSKU, sku))

    # -- Batches

    df["batch_type"] = "butter"
    """used later for storing batch ids for continuous numbering. 
    `Batch` mean different things in different departments. For mozzarella it's a boiling, for mascarpone it is a tank"""
    df["batch_id"] = df["group_id"]  # the same as group_id for butter
    df["absolute_batch_id"] = calc_absolute_batch_id(  # continuous numbering, offset by first_batch_ids_by_type
        boiling_plan_df=df,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )

    # - Saturate boiling plan

    df["boiling"] = df["sku"].apply(lambda sku: delistify(sku.made_from_boilings, single=True))
    df["start"] = None
    df["finish"] = None

    # - Return

    return df


def test():
    df = to_boiling_plan(
        str(get_repo_path() / "app/data/static/samples/by_department/butter/2023-09-03 План по варкам масло.xlsx")
    )
    print(df.iloc[0])
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    print("--")
    print(df)


if __name__ == "__main__":
    test()
