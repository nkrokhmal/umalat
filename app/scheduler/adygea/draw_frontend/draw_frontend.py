from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.adygea.draw_frontend.style import STYLE
from app.scheduler.adygea.draw_frontend.wrap_frontend import wrap_frontend
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.frontend_utils import draw_excel_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    halumi_boilings_count: int = 0,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"adygea": 1},
    date: Optional[datetime] = None,
    workbook: Workbook = None,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        halumi_boilings_count=halumi_boilings_count,
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
        str(get_repo_path() / "app/data/static/samples/by_department/adygea/sample_schedule_adygea.xlsx"),
        halumi_boilings_count=10,
        start_time="07:00",
    )

    output["workbook"].save("/tmp/schedule_adygea.xlsx")
    open_file_in_os("/tmp/schedule_adygea.xlsx")


if __name__ == "__main__":
    test()
