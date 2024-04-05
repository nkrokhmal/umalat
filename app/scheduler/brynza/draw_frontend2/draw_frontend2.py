from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.brynza.draw_frontend2.style import STYLE
from app.scheduler.brynza.draw_frontend2.wrap_frontend2 import wrap_frontend2
from app.scheduler.brynza.draw_frontend.wrap_frontend import wrap_frontend
from app.scheduler.frontend_utils import draw_excel_frontend


def draw_frontend2(
    brynza_boilings: int,
    halumi_boilings: int,
    n_cheese_makers: int = 4,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"brynza": 1},
    date: Optional[datetime] = None,
    workbook: Workbook = None,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend2(
        brynza_boilings=brynza_boilings,
        halumi_boilings=halumi_boilings,
        n_cheese_makers=n_cheese_makers,
        start_time=start_time,
        date=date,
        first_batch_ids_by_type=first_batch_ids_by_type,
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
    output = draw_frontend2(
        brynza_boilings=3,
        halumi_boilings=4,
        n_cheese_makers=4,
        start_time="07:00",
        date=datetime(2021, 1, 1),
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
