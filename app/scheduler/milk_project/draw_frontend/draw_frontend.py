from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.frontend_utils import draw_excel_frontend
from app.scheduler.milk_project.draw_frontend.style import STYLE
from app.scheduler.milk_project.wrap_frontend import wrap_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"milk_project": 1},
    date: Optional[datetime] = None,
    workbook: Workbook = None,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        start_time=start_time,
        first_batch_ids_by_type=first_batch_ids_by_type,
        date=date,
    )

    # - Draw frontend

    output["workbook"] = draw_excel_frontend(
        frontend=output["frontend"],
        style=STYLE,
        open_file=False,
        fn=None,
        wb=workbook,
    )

    # - Return

    return output


def test():
    output = draw_frontend(
        # str(
        #     get_repo_path()
        #     / "app/data/static/samples/by_department/milk_project/2023_12_04_План_по_варкам_милкпроджект (2).xlsx"
        # )
        "/Users/marklidenberg/Desktop/2023.12.23 Маскарпоне и брынза/2023-12-15 План по варкам милкпроджект.xlsx"
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
