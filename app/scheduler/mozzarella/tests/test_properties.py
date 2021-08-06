from app.scheduler import load_schedules
from app.scheduler.mozzarella.properties import *
from pprint import pprint


def test_properties(path, prefix):
    schedules = load_schedules(path, prefix, departments=["mozzarella"])
    props = cast_properties(schedules["mozzarella"])
    pprint(dict(props))
    print(props.drenator_times())
    print(props.cheesemaker_times())


if __name__ == "__main__":
    test_properties(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/static/samples/inputs/by_day/2021-07-10",
        "2021-07-10",
    )
