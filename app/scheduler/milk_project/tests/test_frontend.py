from app.imports.runtime import *
from app.scheduler.milk_project import *
from app.scheduler import draw_excel_frontend


def _test(fn, open_file=False, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_milk_project(fn, open_file=open_file, *args, **kwargs)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs(reset=False)


def test_batch():
    fns = glob.glob(
        config.abs_path(
            "app/data/static/samples/inputs/by_department/milk_project/*.xlsx"
        )
    )
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(utils.tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=True, prefix=str(i))


if __name__ == "__main__":
    # _test(
    #     "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_department/milk_project/План по варкам милкпроджект 3.xlsx",
    #     open_file=True,
    # )

    test_batch()
