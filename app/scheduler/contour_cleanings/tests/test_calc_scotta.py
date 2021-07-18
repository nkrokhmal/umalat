from app.imports.runtime import *
from app.scheduler import *


def _test(path, prefix):
    schedules = load_schedules(
        path,
        prefix=prefix,
        departments=["ricotta"],
    )
    print(schedules.keys())
    print(calc_scotta_input_tanks(schedules))


# if __name__ == "__main__":
#     _test(
#         "/Users/marklidenberg/Yandex.Disk.localized/Загрузки/umalat/2021-07-17/approved",
#         "2021-07-17",
#     )
