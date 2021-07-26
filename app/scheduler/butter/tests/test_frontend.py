from app.imports.runtime import *
from app.scheduler import draw_excel_frontend
from app.scheduler.butter import *


def _test(fn, open_file=False):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_butter(fn, open_file=open_file)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs()


def test_batch():
    fns = glob.glob(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/butter/*.xlsx"
        )
    )
    fns = [fn for fn in fns if "$" not in fn]
    for fn in tqdm.tqdm(fns):
        _test(fn, open_file=False)


if __name__ == "__main__":
    # _test(
    #     "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/butter/План по варкам масло.xlsx",
    #     open_file=True,
    # )
    test_batch()
