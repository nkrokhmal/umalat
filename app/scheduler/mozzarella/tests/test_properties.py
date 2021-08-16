from app.scheduler import load_schedules, load_properties
from app.scheduler.mozzarella.properties import *
from app.scheduler.mozzarella.parser import *
from pprint import pprint
import yaml


def _test_pickle(path, prefix):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(path))
    schedules = load_schedules(path, prefix, departments=["mozzarella"])

    if "manual" in prefix:
        assert "mozzarella" not in schedules
        return

    props = cast_properties(schedules["mozzarella"])
    utils.lazy_tester.log(yaml.dump(dict(props)))
    utils.lazy_tester.assert_logs()


def _test_parser(path, prefix):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(path))
    schedules = load_schedules(path, prefix, departments=["mozzarella"])
    props = load_properties(schedules, path=path, prefix=prefix)["mozzarella"]
    utils.lazy_tester.log(yaml.dump(dict(props)))
    utils.lazy_tester.assert_logs()


def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/inputs/by_day/*"))
    fns = [fn for fn in fns if "$" not in fn]
    for fn in utils.tqdm(fns, desc=lambda v: v):
        _test_pickle(fn, prefix=os.path.basename(fn))
        _test_parser(fn, prefix=os.path.basename(fn))


if __name__ == "__main__":
    utils.lazy_tester.verbose = True

    # _test(
    #     "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/2021-08-06",
    #     "2021-08-06",
    # )

    test_batch()
