from app.imports.runtime import *
from app.enum import LineName
from app.scheduler.mozzarella import make_schedule, make_frontend, STYLE
from app.scheduler.frontend import draw_excel_frontend


def test_batch():
    # fns = glob.glob(
    #     DebugConfig.abs_path("app/data/static/samples/inputs/mozzarella/*.xlsx")
    # )

    fns = [
        DebugConfig.abs_path(fn)
        for fn in [
            "app/data/static/samples/inputs/mozzarella/2021-05-07 План по варкам.xlsx",
            # "app/data/static/samples/inputs/mozzarella/2021-02-28 План по варкам.xlsx",
            # "app/data/static/samples/inputs/mozzarella/2021-02-26 План по варкам.xlsx",
            # "app/data/static/samples/inputs/mozzarella/2021-02-19 План по варкам.xlsx",
            # "app/data/static/samples/inputs/mozzarella/2021-02-17 План по варкам.xlsx",
            # "app/data/static/samples/inputs/mozzarella/2021-02-16 План по варкам.xlsx",
            "app/data/static/samples/inputs/mozzarella/2021-02-09 План по варкам.xlsx",
        ]
    ]
    for fn in tqdm.tqdm(fns):
        _test(fn, open_file=False)


def _test(fn, open_file=False):
    utils.lazy_tester.configure_function_path()

    warnings.filterwarnings("ignore")

    utils.lazy_tester.configure(local_path=os.path.basename(fn))

    start_times = {LineName.WATER: "02:00", LineName.SALT: "06:00"}

    schedule = make_schedule(
        fn, optimize=True, start_times=start_times, first_boiling_id=1
    )
    utils.lazy_tester.log(schedule)

    try:
        frontend = make_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    utils.lazy_tester.log(frontend)

    draw_excel_frontend(
        frontend, open_file=open_file, fn="schedules/schedule.xlsx", style=STYLE
    )
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    _test(
        DebugConfig.abs_path(
            "app/data/static/samples/inputs/mozzarella/2021-05-07 План по варкам.xlsx"
        ),
        open_file=True,
    )
    # test_batch()
