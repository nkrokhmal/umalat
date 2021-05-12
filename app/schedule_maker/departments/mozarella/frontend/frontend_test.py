import os

os.environ["environment"] = "interactive"

from app.imports.runtime import *

warnings.filterwarnings("ignore")

from app.schedule_maker.departments.mozarella import *
from app.schedule_maker.frontend import draw_excel_frontend


def test():
    makedirs("schedules/")
    fn = DebugConfig.abs_path("app/data/inputs/2021-05-07 План по варкам.xlsx")
    start_times = {LineName.WATER: "02:00", LineName.SALT: "06:00"}

    schedule = make_schedule(
        fn, optimize=False, start_times=start_times, first_group_id=1
    )

    try:
        frontend = make_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    draw_excel_frontend(
        frontend, open_file=False, fn="schedules/schedule.xlsx", style=STYLE
    )


if __name__ == "__main__":
    test()
