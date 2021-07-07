from app.imports.runtime import *
from app.scheduler.mascarpone import (
    read_boiling_plan,
    make_schedule,
    wrap_frontend,
    STYLE,
)
from app.scheduler import draw_excel_frontend


def test_mascarpone_batch():
    fns = glob.glob(
        DebugConfig.abs_path("app/data/static/samples/inputs/mascarpone/*.xlsx")
    )
    fns = [fn for fn in fns if "$" not in fn]

    for fn in tqdm.tqdm(fns):
        _test(fn, open_file=False)


def _test(fn, open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    boiling_plan_df = read_boiling_plan(fn)
    schedule = make_schedule(boiling_plan_df, start_batch_id=1)
    utils.lazy_tester.log(schedule)
    frontend = wrap_frontend(schedule)
    utils.lazy_tester.log(frontend)
    draw_excel_frontend(frontend, STYLE, open_file=open_file)
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    # test_mascarpone_batch()
    _test(
        DebugConfig.abs_path(
            "app/data/static/samples/inputs/mascarpone/2021-04-21 План по варкам маскарпоне.xlsx"
        ),
        open_file=True,
    )
