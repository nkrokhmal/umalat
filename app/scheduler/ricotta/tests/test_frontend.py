from app.scheduler.ricotta import *
from app.scheduler import draw_excel_frontend
from app.scheduler.ricotta.algo.schedule import *
from app.scheduler.ricotta.boiling_plan import *
from config import DebugConfig


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(make_frontend_boiling(make_boiling(boiling_model)))


def test_drawing_ricotta(open_file=False):
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_fn = DebugConfig.abs_path(
        "app/data/static/samples/inputs/ricotta/2021-05-15 План по варкам рикотта.xlsx"
    )
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    schedule = make_schedule(boiling_plan_df)
    frontend = make_frontend(schedule)
    draw_excel_frontend(frontend, STYLE, open_file=open_file)


if __name__ == "__main__":
    # test_make_frontend_boiling()
    # test_make_frontend()
    test_drawing_ricotta(open_file=True)
