import os

os.environ["environment"] = "interactive"

from app.scheduler.contour_cleanings.algo.schedule import *
from config import DebugConfig


def test():
    from utils_ak.loguru import configure_loguru_stdout

    import pickle

    fn = "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/outputs/2021-02-09 Моцарелла Расписание.pickle"
    with open(fn, "rb") as f:
        mozarella_schedule = ParallelepipedBlock.from_dict(pickle.load(f))

    print(make_contour_3(mozarella_schedule))


if __name__ == "__main__":
    test()
