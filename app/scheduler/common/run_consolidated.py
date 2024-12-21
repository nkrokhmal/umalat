import os

from typing import Union

from openpyxl import Workbook
from utils_ak.openpyxl.openpyxl_tools import cast_workbook, draw_sheet_sequence
from utils_ak.os.os_tools import makedirs, open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.frontend_utils import prepare_schedule_worksheet
from config import config


def run_consolidated(
    input_path: str,
    prefix: str = "",
    departments: list[str] = [
        "mozzarella",
        "ricotta",
        "milk_project",
        "butter",
        "mascarpone",
    ],
    add_contour_cleanings: bool = True,
    output_path: str = "outputs/",
    wb: Union[Workbook, list] = ["Расписание"],
    open_file: bool = False,
) -> Workbook:

    # - Make directories if not exist

    makedirs(output_path)

    # - Get filenames for departments and contour cleanings

    # -- Get filenames

    fns = [
        os.path.join(
            input_path,
            f"{prefix} Расписание {config.DEPARTMENT_ROOT_NAMES_BY_DEPARTMENT[department]}.xlsx",
        )
        for department in departments
    ]

    if add_contour_cleanings:
        fns.append(
            os.path.join(
                input_path,
                f"{prefix} Расписание контурные мойки.xlsx",
            )
        )

    # -- Filter existing files

    fns = [fn for fn in fns if os.path.exists(fn)]

    # - Prepare workbook

    wb = cast_workbook(wb)
    prepare_schedule_worksheet((wb, "Расписание"))

    # - Draw consolidated schedule

    draw_sheet_sequence((wb, "Расписание"), [(fn, "Расписание") for fn in fns])

    # - Save

    output_fn = os.path.join(output_path, prefix + " Расписание общее.xlsx")
    wb.save(output_fn)

    # - Open file if needed

    if open_file:
        open_file_in_os(output_fn)

    # - Return

    return wb


def test():
    run_consolidated(
        input_path=str(get_repo_path() / "app/data/static/samples/by_day/2024-11-10"),
        add_contour_cleanings=False,
        prefix="2024-11-10",
        open_file=True,
    )


if __name__ == "__main__":
    test()
