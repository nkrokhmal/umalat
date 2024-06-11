from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.brynza.draw_frontend.style import STYLE
from app.scheduler.brynza.draw_frontend.wrap_frontend import wrap_frontend
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.frontend_utils import draw_excel_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    halumi_packings_count: int = 0,
    start_time: str = "07:00",
    date: Optional[datetime] = None,
    workbook: Workbook = None,
) -> dict:

    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        halumi_packings_count=halumi_packings_count,
        start_time=start_time,
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
        str(
            get_repo_path() / "app/data/static/samples/by_department/milk_project/sample_boiling_plan_milk_project.xlsx"
        ),
        halumi_packings_count=2,
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
