from app.scheduler import load_schedules
from app.scheduler.mozzarella.properties import *
from pprint import pprint


def test_properties(path, prefix):
    schedules = load_schedules(path, prefix, departments=["mozzarella"])
    props = parse_schedule(schedules["mozzarella"])
    pprint(dict(props))
    print(props.drenator_times())
    print(props.cheesemaker_times())


if __name__ == "__main__":
    test_properties(
        "/Users/marklidenberg/Yandex.Disk.localized/Загрузки/umalat/2021-07-17/approved",
        "2021-07-17",
    )
