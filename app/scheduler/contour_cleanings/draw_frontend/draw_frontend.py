import os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.contour_cleanings.draw_frontend.style import STYLE
from app.scheduler.contour_cleanings.load_properties_by_department import load_properties_by_department
from app.scheduler.contour_cleanings.make_schedule import make_schedule
from app.scheduler.contour_cleanings.wrap_frontend import wrap_frontend
from app.scheduler.frontend_utils import draw_excel_frontend
from app.scheduler.load_schedules import load_schedules_by_department


def draw_frontend(
    input_path: str,
    output_path: str = "outputs/",
    schedule=None,
    schedules_by_department=None,
    properties_by_department=None,
    prefix="",
    **kwargs,
):
    if not schedule:
        if not properties_by_department:
            if not schedules_by_department:
                schedules_by_department = load_schedules_by_department(input_path, prefix=prefix)

            # todo maybe: need a check here? [@marklidenberg]
            # assert_schedules_presence(
            #     schedules,
            #     raise_if_not_present=["ricotta"],
            #     warn_if_not_present=[
            #         "mozzarella",
            #         "butter",
            #         "adygea",
            #         "milk_project",
            #         "mascarpone",
            #     ],
            # )

            properties_by_department = load_properties_by_department(
                schedules_by_department, path=input_path, prefix=prefix
            )

        schedule = make_schedule(properties_by_department, **kwargs)
    frontend = wrap_frontend(schedule)

    # - Draw frontend

    base_fn = f"{prefix}Расписание контурные мойки.xlsx"
    output_fn = os.path.join(output_path, base_fn)

    workbook = draw_excel_frontend(
        frontend,
        open_file=False,
        fn=output_fn,
        style=STYLE,
    )

    # - Return

    return {"schedule": schedule, "frontend": frontend, "workbook": workbook}


def test():
    draw_frontend(
        input_path=str(get_repo_path() / "app/data/static/samples/by_day/2023-09-03"),
        prefix="2023-09-03",
        open_file=True,
    )


if __name__ == "__main__":
    test()
