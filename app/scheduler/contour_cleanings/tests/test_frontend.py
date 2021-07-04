from app.imports.runtime import *
from app.scheduler import draw_excel_frontend
from app.scheduler.contour_cleanings.algo.schedule import *
from app.scheduler.contour_cleanings.frontend import *


def test(open_file=False):
    utils.configure_loguru_stdout("INFO")
    utils.lazy_tester.configure_function_path()

    from utils_ak.loguru import configure_loguru_stdout

    import pickle

    fn = "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/2021-02-09 Моцарелла Расписание.pickle"
    with open(fn, "rb") as f:
        mozarella_schedule = ParallelepipedBlock.from_dict(pickle.load(f))

    contours = [make_contour_3(mozarella_schedule)]

    frontend = wrap_frontend(contours)

    draw_excel_frontend(frontend, STYLE, open_file=open_file)


if __name__ == "__main__":
    test(open_file=True)
