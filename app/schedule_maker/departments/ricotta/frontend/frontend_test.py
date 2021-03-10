import os

os.environ["environment"] = "interactive"

from app.schedule_maker import *


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(make_frontend_boiling(make_boiling(boiling_model)))


def test_make_frontend():
    schedule = make_schedule()
    frontend = make_frontend(schedule)
    print(frontend)


def test_drawing():
    schedule = make_schedule()
    frontend = make_frontend(schedule)
    draw_excel_frontend(frontend, RICOTTA_STYLE, open_file=True)


if __name__ == "__main__":
    test_make_frontend_boiling()
    test_make_frontend()

    test_drawing()
