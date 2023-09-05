from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.frontend_utils import draw_excel_frontend
from app.scheduler.mascarpone.draw_frontend.style import STYLE
from app.scheduler.mascarpone.draw_frontend.wrap_frontend import wrap_frontend
from app.scheduler.mascarpone.to_boiling_plan import BoilingPlanLike


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    start_times_by_line: dict = {1: "07:00", 2: "08:00"},
    first_batch_ids_by_type: dict = {"cottage_cheese": 1, "cream": 1, "mascarpone": 1, "cream_cheese": 1},
    date: Optional[datetime] = None,
    workbook: Workbook = None,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        start_times_by_line=start_times_by_line,
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
        # str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/План по варкам.xlsx"),
        str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/2023-09-05 Расписание маскарпоне.xlsx"),
        start_times_by_line={1: "06:00", 2: "06:30"},
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
