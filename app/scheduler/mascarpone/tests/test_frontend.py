from app.imports.runtime import *
from app.scheduler.mascarpone import *


def test_batch():
    fns = glob.glob(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/mascarpone/*.xlsx"
        )
    )
    fns = [fn for fn in fns if "$" not in fn]

    for fn in utils.tqdm(fns, desc=lambda fn: fn):
        _test(fn, open_file=False)


def _test(fn, open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_mascarpone(fn, open_file=open_file)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    _test(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/mascarpone/План по варкам маскарпоне 1.xlsx"
        ),
        open_file=True,
    )

    # test_batch()
#
