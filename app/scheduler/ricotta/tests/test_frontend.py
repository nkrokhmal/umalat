from app.imports.runtime import *
from app.scheduler.ricotta import *
from app.scheduler import draw_excel_frontend
from app.scheduler.ricotta.algo.schedule import *
from app.scheduler.ricotta.boiling_plan import *


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(wrap_boiling(make_boiling(boiling_model)))


def test_drawing_ricotta(open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    boiling_plan_fn = DebugConfig.abs_path(
        "app/data/static/samples/inputs/ricotta/2021-05-15 План по варкам рикотта.xlsx"
    )
    utils.lazy_tester.configure(local_path=os.path.basename(boiling_plan_fn))

    boiling_plan_df = read_boiling_plan(boiling_plan_fn)

    schedule = make_schedule(boiling_plan_df)
    utils.lazy_tester.log(schedule)
    frontend = wrap_frontend(schedule)

    utils.lazy_tester.log(frontend)
    draw_excel_frontend(frontend, STYLE, open_file=open_file)

    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    # test_make_frontend_boiling()
    # test_make_frontend()
    test_drawing_ricotta(open_file=False)
