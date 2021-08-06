from app.imports.runtime import *
from app.enum import LineName
from app.scheduler.mozzarella import run_mozzarella


def test_batch():
    fns = glob.glob(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/mozzarella/*.xlsx"
        )
    )
    fns = [fn for fn in fns if "$" not in fn]
    for fn in utils.tqdm(fns, desc=lambda v: v):
        _test(fn, open_file=False)


def _test(fn, open_file=False):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_mozzarella(fn, open_file=open_file)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    _test(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/mozzarella/План по варкам моцарелла 7.xlsx"
            # "app/data/static/samples/inputs/by_day/2021-08-06/2021-08-06 Расписание моцарелла.xlsx"
        ),
        open_file=True,
    )
    # test_batch()
