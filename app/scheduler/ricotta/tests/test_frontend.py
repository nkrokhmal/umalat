from app.imports.runtime import *
from app.models import RicottaBoiling, cast_model
from app.scheduler.ricotta.algo import make_boiling
from app.scheduler.ricotta.frontend import wrap_boiling
from app.scheduler.ricotta.runner import run_ricotta


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(wrap_boiling(make_boiling(boiling_model)))


def _test(fn, open_file=False, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_ricotta(fn, open_file=open_file, first_batch_id=100)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


def test_batch():
    fns = glob.glob(
        config.abs_path("app/data/static/samples/inputs/by_department/ricotta/*.xlsx")
    )
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(utils.tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


if __name__ == "__main__":
    _test(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/ricotta/План по варкам рикотта.xlsx",
        open_file=True,
    )
    # test_batch()
