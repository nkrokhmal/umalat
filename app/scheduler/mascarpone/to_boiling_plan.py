from typing import Union

import pandas as pd

from openpyxl import Workbook
from utils_ak.builtin import delistify
from utils_ak.openpyxl.openpyxl_tools import cast_workbook
from utils_ak.pandas import mark_consecutive_groups

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import MascarponeSKU, cast_model
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.update_absolute_batch_id import update_absolute_batch_id
from app.utils.mascarpone.boiling_plan_read import BoilingPlanReader


def to_boiling_plan(
    boiling_plan_source: BoilingPlanLike,
    first_batch_ids_by_type: dict = {"cottage_cheese": 1, "cream": 1, "mascarpone": 1, "cream_cheese": 1},
) -> pd.DataFrame:
    """
    :param boiling_plan_source: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """

    if isinstance(boiling_plan_source, pd.DataFrame):
        # already a dataframe
        return boiling_plan_source

    # - Read boiling plan

    reader = BoilingPlanReader(wb=boiling_plan_source, first_batches=first_batch_ids_by_type)
    df = reader.parse()

    # - Return

    return df


def test():
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    df = to_boiling_plan(
        str(
            get_repo_path()
            / "app/data/static/samples/by_department/mascarpone/2023-09-13 Расписание маскарпоне (2).xlsx"
        )
    )
    print(df)


if __name__ == "__main__":
    test()
