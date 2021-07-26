from app.imports.runtime import *
from app.scheduler import draw_excel_frontend
from app.scheduler.contour_cleanings.algo.schedule import *
from app.scheduler.contour_cleanings.frontend import *
from app.scheduler.contour_cleanings import run_contour_cleanings


def test_batch():
    paths = glob.glob(
        config.abs_path(
            "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/*"
        )
    )
    for path in tqdm.tqdm(paths):
        _test(path, open_file=False)


def _test(path, open_file=False, prefix=None):
    logger.info("Test", path=path)
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()
    utils.lazy_tester.configure(local_path=os.path.basename(path))
    prefix = prefix or os.path.basename(path)
    outputs = run_contour_cleanings(
        path,
        prefix=prefix,
        open_file=open_file,
        adygea_end_time="14:00:00",
    )
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    # _test(
    #     "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/2021-07-16",
    #     prefix="2021-07-16",
    #     open_file=True,
    # )

    test_batch()
