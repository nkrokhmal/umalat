import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.ricotta import *
from app.schedule_maker import draw_excel_frontend


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(make_frontend_boiling(make_boiling(boiling_model)))


def test_make_frontend():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = generate_random_boiling_plan()
    schedule = make_schedule(boiling_plan_df)
    frontend = make_frontend(schedule)
    print(frontend)


def test_drawing():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = generate_random_boiling_plan()
    schedule = make_schedule(boiling_plan_df)
    frontend = make_frontend(schedule)
    draw_excel_frontend(frontend, RICOTTA_STYLE, open_file=True)


if __name__ == "__main__":
    test_make_frontend_boiling()
    test_make_frontend()

    test_drawing()
