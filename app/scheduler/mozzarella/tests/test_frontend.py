from app.imports.runtime import *  # isort: skip
from app.enum.line_name import LineName
from app.scheduler.mozzarella import run_mozzarella


def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/inputs/by_department/mozzarella/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(utils.tqdm(fns, desc=lambda v: v)):
        if "несохраненное" in fn:
            continue

        _test(fn, open_file=False, prefix=str(i))

    # try:
    #     _test(config.abs_path("app/data/static/samples/inputs/by_department/mozzarella/План по варкам моцарелла 5 расписание несохраненное.xlsx"))
    # except Exception as e:
    #     assert str(e) == "Ошибка в чтении плана варок. Если вы работаете с файлом расписания, убедитесь что вы его сохранили перед тем, как залить на сайт"


def _test(fn, *args, **kwargs):
    utils.lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    utils.lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_mozzarella(fn, *args, **kwargs)
    utils.lazy_tester.log(outputs["schedule"])
    utils.lazy_tester.assert_logs(reset=False)


if __name__ == "__main__":
    utils.configure_loguru(level="DEBUG")
    _test(
        "/Users/arsenijkadaner/Desktop/2022-10-19 План по варкам моцарелла.xlsx",
        start_times={LineName.WATER: "08:00", LineName.SALT: "05:00"},
        first_batch_id=100,
        open_file=True,
        prefix="new5",
        optimize=True,
    )
    # test_batch()
