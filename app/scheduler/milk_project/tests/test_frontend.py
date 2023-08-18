import glob
import os
import warnings

import tqdm

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester

from config import config


def _test(fn, open_file=False, *args, **kwargs):
    lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_milk_project(fn, open_file=open_file, *args, **kwargs)
    lazy_tester.log(outputs["schedule"])
    lazy_tester.assert_logs(reset=False)


def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/inputs/by_department/milk_project/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


if __name__ == "__main__":
    _test(
        "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/milk_project/План по варкам милкпроджект 3.xlsx",
        open_file=True,
    )

    # test_batch()
