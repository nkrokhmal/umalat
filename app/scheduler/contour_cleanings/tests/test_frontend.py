import glob
import os

import tqdm

from loguru import logger
from utils_ak.lazy_tester.lazy_tester_class import lazy_tester

from config import config


def test_batch():
    paths = glob.glob(
        config.abs_path(
            "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/by_day/*"
        )
    )
    for i, path in enumerate(tqdm(paths, desc=lambda v: v)):
        _test(path, open_file=False)


def _test(path, open_file=False, prefix=None, *args, **kwargs):
    logger.info("Test", path=path)
    configure_loguru_stdout("INFO")
    lazy_tester.configure_function_path()
    lazy_tester.configure(local_path=os.path.basename(path))
    prefix = prefix or os.path.basename(path)
    outputs = run_contour_cleanings(path, prefix=prefix, open_file=open_file, *args, **kwargs)
    lazy_tester.log(outputs["schedule"])
    lazy_tester.assert_logs()


if __name__ == "__main__":
    # _test(
    #     "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/by_day/2021-07-10-manual",
    #     prefix="2021-07-10-manual",
    #     open_file=True,
    #     is_tomorrow_day_off=True,
    # )

    test_batch()
