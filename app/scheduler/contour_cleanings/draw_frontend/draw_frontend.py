import os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.contour_cleanings.draw_frontend.style import STYLE
from app.scheduler.contour_cleanings.load_properties_by_department import load_properties_by_department
from app.scheduler.contour_cleanings.make_schedule import make_schedule
from app.scheduler.contour_cleanings.wrap_frontend import wrap_frontend
from app.scheduler.frontend_utils import draw_excel_frontend


def draw_frontend(
    input_path: str,
    output_path: str = "outputs/",
    schedule=None,
    properties_by_department: dict = {},
    prefix="",
    open_file: bool = False,
    **kwargs,
):
    # - Make frontend

    properties_by_department = properties_by_department or load_properties_by_department(path=input_path, prefix=prefix)

    schedule = schedule or make_schedule(properties_by_department, **kwargs)
    frontend = wrap_frontend(schedule)

    # - Draw frontend

    base_fn = f"{prefix}Расписание контурные мойки.xlsx"
    output_fn = os.path.join(output_path, base_fn)

    workbook = draw_excel_frontend(
        frontend,
        open_file=open_file,
        fn=output_fn,
        style=STYLE,
    )

    # - Return

    return {"schedule": schedule, "frontend": frontend, "workbook": workbook}


def test():
    import warnings

    warnings.filterwarnings("ignore")

    draw_frontend(
        input_path="""/Users/marklidenberg/Documents/coding/repos/umalat/app/data/dynamic/2024-03-15/approved""",
        prefix="2024-03-15",
        open_file=True,
        is_today_day_off=True,
    )


if __name__ == "__main__":
    test()
