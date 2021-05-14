import os

os.environ["environment"] = "interactive"

from app.imports.runtime import *

warnings.filterwarnings("ignore")

from app.scheduler.mozzarella import *
from app.scheduler.frontend import draw_excel_frontend


def test():
    utils.clock.enable()
    makedirs("schedules/")
    fn = DebugConfig.abs_path(
        "app/data/samples/inputs/mozzarella/2021-05-07 План по варкам.xlsx"
    )
    start_times = {LineName.WATER: "02:00", LineName.SALT: "06:00"}

    schedule = make_schedule(
        fn, optimize=False, start_times=start_times, first_group_id=1
    )

    try:
        frontend = make_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    draw_excel_frontend(
        frontend, open_file=True, fn="schedules/schedule.xlsx", style=STYLE
    )
    print(utils.clock.stats())


if __name__ == "__main__":
    test()
