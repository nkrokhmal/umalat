from utils_ak.os.os_tools import makedirs

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.butter.algo.schedule import make_schedule
from app.scheduler.butter.boiling_plan.boiling_plan import read_boiling_plan
from app.scheduler.butter.frontend.frontend import wrap_frontend
from app.scheduler.butter.frontend.style import STYLE
from app.scheduler.submit import submit_schedule


def run_butter(
    boiling_plan_fn: str = None,
    schedule=None,
    open_file: bool = False,
    start_time: str = None,  # "07:00"
    path: str = "outputs/",
    prefix: str = "",
):
    makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    start_time = start_time or "07:00"

    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    res = submit_schedule("масло", schedule, frontend, prefix, STYLE, path=path, open_file=open_file)
    res["boiling_plan_df"] = boiling_plan_df
    return res


def test():
    run_butter(
        str(get_repo_path() / "app/data/static/samples/inputs/by_department/butter/План по варкам масло 1.xlsx"),
        open_file=True,
    )


if __name__ == "__main__":
    test()
