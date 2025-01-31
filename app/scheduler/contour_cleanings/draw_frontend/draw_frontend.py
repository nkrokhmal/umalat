import os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.frontend_utils import draw_excel_frontend
from app.scheduler.contour_cleanings.draw_frontend.style import STYLE
from app.scheduler.contour_cleanings.load_properties_by_department import load_properties_by_department
from app.scheduler.contour_cleanings.make_schedule import make_schedule
from app.scheduler.contour_cleanings.wrap_frontend import wrap_frontend


def draw_frontend(
    input_path: str,
    output_path: str = "outputs/",
    schedule=None,
    properties: dict = {},
    prefix="",
    open_file: bool = False,
    naslavuchich: bool = True,
    basement_brine: bool = True,
    goat_cream: bool = True,
    air_knives: bool = True,
    hohland: bool = True,
    is_today_day_off: bool = False,
):

    # - Make frontend

    properties = properties or load_properties_by_department(path=input_path, prefix=prefix)
    schedule = schedule or make_schedule(
        properties,
        naslavuchich=naslavuchich,
        basement_brine=basement_brine,
        goat_cream=goat_cream,
        air_knives=air_knives,
        hohland=hohland,

        is_today_day_off=is_today_day_off,
    )
    frontend = wrap_frontend(schedule)

    # - Draw frontend

    base_fn = f"{prefix} Расписание контурные мойки.xlsx"
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

    # draw_frontend(
    #     input_path=str(get_repo_path() / "app/data/static/samples/by_day/2024-11-10"),
    #     prefix="2024-11-10",
    #     is_today_day_off=False,
    #     open_file=True,
    # )

    draw_frontend(
        input_path=str(get_repo_path() / "app/data/static/samples/by_day/sample"),
        prefix="sample",
        is_today_day_off=False,
        open_file=True,
    )
    # import glob
    # p
    # import tqdm
    #
    # for dirname in tqdm.tqdm(
    #     sorted(glob.glob("""/Users/marklidenberg/Desktop/inbox/2024.04.06 contour_cleanings/*"""))
    # ):
    #     date = dirname.split("/")[-1]
    #     print(date)
    #     draw_frontend(
    #         input_path=os.path.join(dirname, "approved"),
    #         prefix=date,
    #         open_file=False,
    #         is_today_day_off=False,
    #     )


if __name__ == "__main__":
    test()
