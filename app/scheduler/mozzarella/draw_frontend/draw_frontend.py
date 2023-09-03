from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.frontend_utils import draw_excel_frontend
from app.scheduler.mozzarella.draw_frontend.style import STYLE
from app.scheduler.mozzarella.wrap_frontend import wrap_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    date: Optional[datetime] = None,
    workbook: Workbook = None,
    optimize=True,
    exact_melting_time_by_line=None,
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    *args,
    **kwargs,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        start_time=start_time,
        first_batch_ids_by_type=first_batch_ids_by_type,
        date=date,
        optimize=optimize,
        exact_melting_time_by_line=exact_melting_time_by_line,
        saturate=saturate,
        normalization=normalization,
        validate=validate,
        *args,
        **kwargs,
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
            get_repo_path()
            / "app/data/static/samples/inputs/by_department/mozzarella/План по варкам моцарелла 4 расписание.xlsx"
        )
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
