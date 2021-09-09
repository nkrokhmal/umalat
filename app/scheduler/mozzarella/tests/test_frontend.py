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
    for i, fn in enumerate(utils.tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


def _test(fn, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_mozzarella(fn, *args, **kwargs)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    _test(
        config.abs_path(
            "/Users/marklidenberg/Desktop/2021-09-07 Расписание моцарелла.xlsx"
        ),
        start_times={LineName.WATER: "06:00", LineName.SALT: "07:00"},
        first_boiling_id=72,
        open_file=False,
        prefix="new",
    )
    # test_batch()
