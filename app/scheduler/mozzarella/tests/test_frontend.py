from app.imports.runtime import *  # isort: skip
from app.enum import LineName
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
        "/Users/arsenijkadaner/Desktop/2023-06-02 План по варкам моцарелла.xlsx",
        start_times={LineName.WATER: "06:00", LineName.SALT: "06:00"},
        first_batch_id=1,
        open_file=True,
        prefix="new6",
        optimize=False,

        start_configuration=[
            "Моцарелла в воде", # 1
            "Моцарелла в воде", # 2
            "Пицца чиз", # 13
            # "Пицца чиз", # 14
            # "Моцарелла в воде", # 3
            # "Пицца чиз", # 15
            # "Моцарелла в воде", # 4
            # "Пицца чиз", # 16
            # "Моцарелла в воде", # 5
            # "Пицца чиз", # 17
            # "Моцарелла в воде", # 6
            # "Пицца чиз", # 18
            # "Пицца чиз", # 19
            # "Моцарелла в воде", # 7
            # "Пицца чиз", # 20
            # "Моцарелла в воде", # 8
            # "Пицца чиз", # 21
            # 'Пицца чиз', # 22
            # 'Моцарелла в воде', # 9
            # 'Пицца чиз', # 23
            # 'Моцарелла в воде', # 10
            # 'Пицца чиз', # 24
            # 'Пицца чиз', # 25
            # 'Моцарелла в воде', # 11
            # 'Пицца чиз', # 26
            # 'Моцарелла в воде', # 12
            # 'Пицца чиз', # 27
            # 'Пицца чиз', # 28
            # 'Пицца чиз', # 29
        ],
    )
    # test_batch()
