from app.scheduler import load_schedules
from app.scheduler.ricotta.properties import *
from pprint import pprint


def test_properties(path, prefix):
    schedules = load_schedules(path, prefix, departments=["ricotta"])
    props = parse_schedule(schedules["ricotta"])
    pprint(dict(props))


if __name__ == "__main__":
    test_properties(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/sample1",
        "sample1",
    )
