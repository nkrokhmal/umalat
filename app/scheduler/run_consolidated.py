import os

from openpyxl import Workbook
from utils_ak.openpyxl.openpyxl_tools import cast_workbook, draw_sheet_sequence
from utils_ak.os.os_tools import makedirs, open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.frontend_utils import prepare_schedule_worksheet
from config import config


def run_consolidated(
    input_path: str,
    prefix: str = "",
    departments: list[str] = None,
    add_contour_cleanings: bool = True,
    output_path: str = "outputs/",
    wb: Workbook = None,
    open_file: bool = False,
):
    departments = departments or [
        "mozzarella",
        "ricotta",
        "milk_project",
        "butter",
        "mascarpone",
    ]
    makedirs(output_path)

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

    fns = [fn for fn in fns if os.path.exists(fn)]
    wb = wb or ["Расписание"]
    wb = cast_workbook(wb)
    prepare_schedule_worksheet((wb, "Расписание"))
    draw_sheet_sequence((wb, "Расписание"), [(fn, "Расписание") for fn in fns])
    output_fn = os.path.join(output_path, prefix + " Расписание общее.xlsx")
    wb.save(output_fn)
    if open_file:
        open_file_in_os(output_fn)
    return wb


def test():
    run_consolidated(
        input_path=str(get_repo_path() / "app/data/static/samples/by_day/2023-09-03"),
        add_contour_cleanings=False,
        prefix="2023-09-03",
        open_file=True,
    )


if __name__ == "__main__":
    test()
