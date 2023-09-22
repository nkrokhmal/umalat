from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.frontend_utils import draw_excel_frontend
from app.scheduler.mozzarella.draw_frontend.style import STYLE
from app.scheduler.mozzarella.wrap_frontend import wrap_frontend


def draw_frontend(
    boiling_plan: BoilingPlanLike,
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
            / "app/data/static/samples/by_department/mozzarella/2023-09-22 План по варкам моцарелла.xlsx"
        ),
        start_times={LineName.WATER: "06:00", LineName.SALT: "05:00"},
        exact_melting_time_by_line=LineName.WATER,
        optimize=True,
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
