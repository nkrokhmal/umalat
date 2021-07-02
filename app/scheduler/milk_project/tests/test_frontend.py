from app.imports.runtime import *
from app.scheduler import draw_excel_frontend
from app.scheduler.milk_project.algo.schedule import *
from app.scheduler.milk_project.boiling_plan import *
from app.scheduler.milk_project.frontend import *


def test_drawing_milk_project(boiling_plan_obj=None, open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    if not boiling_plan_obj:
        boiling_plan_df = generate_random_boiling_plan()
        utils.lazy_tester.configure(local_path="random")
    else:
        fn = boiling_plan_obj
        boiling_plan_df = read_boiling_plan(fn)
        utils.lazy_tester.configure(local_path=os.path.basename(fn))

    schedule = make_schedule(boiling_plan_df)
    utils.lazy_tester.log(schedule)
    frontend = wrap_frontend(schedule)

    utils.lazy_tester.log(frontend)
    draw_excel_frontend(frontend, STYLE, open_file=open_file)

    utils.lazy_tester.assert_logs()


def test_samples():
    fns = glob.glob(
        DebugConfig.abs_path("app/data/static/samples/inputs/milk_project/*.xlsx")
    )
    fns = [fn for fn in fns if "$" not in fn]
    for fn in fns:
        test_drawing_milk_project(fn, open_file=True)


if __name__ == "__main__":
    # test_drawing_milk_project(open_file=True)
    test_samples()
