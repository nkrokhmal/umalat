from app.imports.runtime import *
from app.scheduler.butter.parser import parse_properties


def test_batch():
    fns = glob.glob(
        config.abs_path(
            "app/data/static/samples/outputs/by_department/butter/*.xlsx"
        )
    )
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(utils.tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


def _test(fn, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    output = parse_properties(fn)
    utils.lazy_tester.log(output)
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    utils.configure_loguru(level="DEBUG")
    test_batch()

