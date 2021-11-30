from app.imports.runtime import *
from app.scheduler.adygea import *


def _test(fn, open_file=False):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_adygea(fn, open_file=open_file)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs(reset=False)


def test_batch():
    fns = glob.glob(
        config.abs_path("app/data/static/samples/inputs/by_department/adygea/*.xlsx")
    )
    fns = [fn for fn in fns if "$" not in fn]
    for fn in utils.tqdm(fns, desc=lambda v: v):
        _test(fn, open_file=False)


if __name__ == "__main__":
    _test(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/adygea/План по варкам адыгейский 2.xlsx",
        open_file=True,
    )
    # test_batch()