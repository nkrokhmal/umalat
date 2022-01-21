from app.scheduler import load_schedules
from app.scheduler.mascarpone.properties import *
from pprint import pprint


def test_batch():
    paths = glob.glob(
        config.abs_path(
            "app/data/static/samples/inputs/by_day/*"
        )
    )
    paths = [fn for fn in paths if "$" not in fn]
    prefixes = [os.path.basename(fn) for fn in paths]

    for i, fn in enumerate(utils.tqdm(paths, desc=lambda v: v)):
        _test(paths[i], prefixes[i], open_file=False, prefix=str(i))


def _test(path, path_prefix, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(path + path_prefix))

    schedules = load_schedules(path, path_prefix, departments=["mascarpone"])
    outputs = cast_properties(schedules["mascarpone"])
    utils.lazy_tester.log(outputs)
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    utils.lazy_tester.verbose = True
    test_batch()