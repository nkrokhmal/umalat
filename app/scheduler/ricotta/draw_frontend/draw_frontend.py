from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.openpyxl import init_workbook, set_dimensions, set_zoom
from utils_ak.os import open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.frontend_utils import draw_excel_frontend
from app.scheduler.ricotta.draw_frontend.style import STYLE
from app.scheduler.ricotta.draw_frontend.wrap_frontend import wrap_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"ricotta": 1},
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

    # - Prepare workbook

    if not workbook:
        workbook = init_workbook(["Расписание"])

    if "Расписание" not in workbook.sheetnames:
        workbook.create_sheet("Расписание")

    # - Set dimensions
    ws = workbook["Расписание"]
    set_zoom(ws, 55)
    set_dimensions(ws, "column", range(1, 5), 21)
    set_dimensions(ws, "column", range(5, 288 * 2), 2.4)
    set_dimensions(ws, "row", range(1, 2), 25)
    set_dimensions(ws, "row", range(2, 220), 50)

    # - Draw frontend

    output["workbook"] = draw_excel_frontend(
        frontend=output["frontend"], style=STYLE, open_file=False, fn=None, wb=workbook, init=False
    )

    # - Return

    return output


def test():
    output = draw_frontend(
        str(get_repo_path() / "app/data/tests/ricotta/boiling.xlsx"),
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
