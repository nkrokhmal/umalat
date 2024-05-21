import pandas as pd

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.utils.mascarpone.boiling_plan_read import BoilingPlanReader


def to_boiling_plan(
    boiling_plan_source: BoilingPlanLike,
    first_batch_ids_by_type: dict = {
        "cream": 1,
        "mascarpone": 1,
        "cream_cheese": 1,
        "cottage_cheese": 1,
    },
    unwind: bool = False,
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

    Custom columns:
    - group: Union["cream", "mascarpone", "cream_cheese", "robiola", "cottage_cheese"]. Берется по названию SKU
    - semifinished_gruop: Union["cream", "mascarpone", "cream_cheese", "robiola"]. Совпадает с group, только `cottage_cheese` относится к `robiola`
    - line: "кремчиз" или "маскарпоне". На линии кремчиз делаются группы кремчиз, творожный, робиола и мб сливки. На линии маскарпоне делаются маскарпоне и мб сливки
    - batch_type: совпадает с group

    - boiling_type: "68.0,", "70.0, Огурец" - жирность и мб добавка

    - kg: сколько хотим делать такого sku
    - input_kg: сколько сырья приходит на вход на варку
    - output_kg: сколько полуфабриката получаем на выходе с варки

    - washing: нужна ли мойка после данной варки. Указывается руками в плане варок
    """

    if isinstance(boiling_plan_source, pd.DataFrame):
        # already a dataframe
        return boiling_plan_source

    # - Read boiling plan

    df = BoilingPlanReader(
        wb=boiling_plan_source,
        first_batches=first_batch_ids_by_type,
    ).parse(unwind=unwind)

    # - Fix bugged ids

    # -- batch_id and absolute_batch_id

    df.pop("absolute_batch_id")  # it's wrong
    df["batch_id"] = df.pop("block_id")
    df["absolute_batch_id"] = df["batch_id"]
    for batch_type, first_id in first_batch_ids_by_type.items():
        df.loc[df["group"] == batch_type, "absolute_batch_id"] = (
            df.loc[df["group"] == batch_type, "batch_id"] + first_id - 1
        )
    df["boiling_id"] = df.pop("group_id")

    # - Return

    return df


def test():
    df = to_boiling_plan(
        str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/sample_schedule.xlsx"),
        first_batch_ids_by_type={
            "cream": 1,
            "mascarpone": 10,
            "cream_cheese": 100,
            "cottage_cheese": 1000,
        },
    )
    print(df.iloc[0])
    print("-" * 100)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    print(df)


if __name__ == "__main__":
    test()
