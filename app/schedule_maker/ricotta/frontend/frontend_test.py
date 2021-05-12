import os

os.environ["environment"] = "interactive"

from app.schedule_maker.ricotta import *
from app.schedule_maker import draw_excel_frontend
from app.schedule_maker.ricotta.algo.schedule import *
from app.schedule_maker.ricotta.boiling_plan import *
from config import DebugConfig


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(make_frontend_boiling(make_boiling(boiling_model)))


def test_make_frontend(boiling_plan_df):
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    schedule = make_schedule(boiling_plan_df)
    frontend = make_frontend(schedule)
    print(frontend)


def test_drawing(boiling_plan_df):
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    schedule = make_schedule(boiling_plan_df)
    frontend = make_frontend(schedule)
    draw_excel_frontend(frontend, STYLE, open_file=True)


if __name__ == "__main__":
    test_make_frontend_boiling()
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/ricotta/sample_boiling_plan.xlsx")
    )
    test_make_frontend(boiling_plan_df)
    test_drawing(boiling_plan_df)
