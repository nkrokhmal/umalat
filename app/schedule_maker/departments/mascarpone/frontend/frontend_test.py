import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.mascarpone import *
from app.schedule_maker import draw_excel_frontend
from config import DebugConfig


def test_make_frontend():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path(
            "app/data/inputs/mascarpone/2021_04_18_План_по_варкам_маскарпоне_12.xlsx"
        )
    )
    schedule = make_schedule(boiling_plan_df.iloc[-2:])
    frontend = make_frontend(schedule)
    print(frontend)


def test_drawing():
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path(
            "app/data/inputs/mascarpone/2021-04-20 План по варкам маскарпоне (1).xlsx"
        )
    )
    schedule = make_schedule(boiling_plan_df, start_batch_id=1)
    frontend = make_frontend(schedule)
    draw_excel_frontend(frontend, MASCARPONE_STYLE, open_file=True)


if __name__ == "__main__":
    # test_make_frontend()
    test_drawing()
