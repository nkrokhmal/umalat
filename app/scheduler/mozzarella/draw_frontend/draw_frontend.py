from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.loguru import configure_loguru
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
    optimize_start_configurations=True,
    optimize_water_gaps=True,
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    # - Make schedule basic kwargs
    exact_start_time_line_name=None,
    optimize_cleanings=False,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    start_configuration=None,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        first_batch_ids_by_type=first_batch_ids_by_type,
        optimize_start_configurations=optimize_start_configurations,
        optimize_water_gaps=optimize_water_gaps,
        saturate=saturate,
        normalization=normalization,
        validate=validate,
        # - Make schedule basic kwargs
        date=date,
        optimize_cleanings=optimize_cleanings,
        start_times=start_times,
        start_configuration=start_configuration,
        exact_start_time_line_name=exact_start_time_line_name,
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
    # - Ignore warnings

    import warnings

    warnings.filterwarnings("ignore")

    # - Configure loguru

    configure_loguru()

    # - Draw frontend

    output = draw_frontend(
        # str(
        #     get_repo_path()
        #     / "app/data/static/samples/by_department/mozzarella/2023-09-22 План по варкам моцарелла.xlsx"
        # ),
        "/Users/arsenijkadaner/Desktop/моцарелла/2023-11-22 План по варкам моцарелла.xlsx",
        start_times={LineName.WATER: "08:30", LineName.SALT: "06:00"},
        exact_start_time_line_name=LineName.SALT,
        optimize_start_configurations=False,
        optimize_water_gaps=False,
        first_batch_ids_by_type={"mozzarella": 1},
    )

    output["workbook"].save("test.xlsx")
    open_file_in_os("test.xlsx")


if __name__ == "__main__":
    test()
