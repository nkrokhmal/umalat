from app.scheduler import load_schedules
from app.scheduler.mascarpone.properties import *
from pprint import pprint


def test_properties(path, prefix):
    schedules = load_schedules(path, prefix, departments=["mascarpone"])
    props = cast_properties(schedules["mascarpone"])
    pprint(dict(props))


if __name__ == "__main__":
    test_properties(
        "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-11-28/approved",
        "2021-11-28",
    )
