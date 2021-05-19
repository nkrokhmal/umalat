from app.scheduler.mascarpone import (
    read_boiling_plan,
    make_schedule,
    make_frontend,
    MASCARPONE_STYLE,
)
from app.scheduler import draw_excel_frontend
from config import DebugConfig


def test_drawing_mascarpone(open_file=False):
    from utils_ak.loguru import configure_loguru_stdout

    configure_loguru_stdout("INFO")
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path(
            "app/data/static/samples/inputs/mascarpone/2021-04-21 План по варкам маскарпоне.xlsx"
        )
    )
    schedule = make_schedule(boiling_plan_df, start_batch_id=1)
    frontend = make_frontend(schedule)
    draw_excel_frontend(frontend, MASCARPONE_STYLE, open_file=open_file)


if __name__ == "__main__":
    test_drawing_mascarpone(open_file=True)
