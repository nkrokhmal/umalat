from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.butter.draw_frontend.style import STYLE
from app.scheduler.butter.to_boiling_plan import BoilingPlanLike
from app.scheduler.butter.wrap_frontend import wrap_frontend
from app.scheduler.frontend_utils import draw_excel_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"butter": 1},
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
        str(get_repo_path() / "app/data/static/samples/inputs/by_department/butter/План по варкам масло 1.xlsx")
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
