from app.imports.runtime import *
from app.enum import LineName
from app.scheduler.mozzarella import make_schedule, make_frontend, STYLE
from app.scheduler.frontend import draw_excel_frontend


def test():
    warnings.filterwarnings("ignore")

    fn = DebugConfig.abs_path(
        "app/data/static/samples/inputs/mozzarella/2021-02-28 План по варкам.xlsx"
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
        frontend, open_file=False, fn="schedules/schedule.xlsx", style=STYLE
    )


if __name__ == "__main__":
    test()
