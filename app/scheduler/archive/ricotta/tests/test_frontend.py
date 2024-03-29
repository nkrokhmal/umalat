import glob
import os
import warnings

import tqdm

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester

from app.models import RicottaBoiling, cast_model
from config import config


def test_make_frontend_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(wrap_boiling(make_boiling(boiling_model)))


def _test(fn, open_file=False, *args, **kwargs):
    lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_ricotta(fn, open_file=open_file, first_batch_id=100)
    lazy_tester.log(outputs["schedule"])
    lazy_tester.assert_logs()


def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/by_department/ricotta/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


if __name__ == "__main__":
    _test(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/by_department/ricotta/План по варкам рикотта.xlsx",
        open_file=True,
    )
    # test_batch()
