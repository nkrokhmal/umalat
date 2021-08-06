from app.imports.runtime import *
from utils_ak.block_tree import *
import flask


def load_schedules(path, prefix, departments=None):
    schedules = {}
    departments = departments or []

    for department, name in config.DEPARTMENT_NAMES.items():
        if departments and department not in departments:
            continue
        fn = os.path.join(path, f"{prefix} Расписание {name}.pickle")
        if os.path.exists(fn):
            with open(fn, "rb") as f:
                schedules[department] = ParallelepipedBlock.from_dict(pickle.load(f))

    return schedules


def assert_schedules_presence(
    schedules, raise_if_not_present=None, warn_if_not_present=None
):
    raise_if_not_present = raise_if_not_present or []
    warn_if_not_present = warn_if_not_present or []

    for department in raise_if_not_present:
        if department not in schedules:
            raise Exception(
                f"Не найдено расписание для {config.DEPARTMENT_NAMES[department]}"
            )

    for department in warn_if_not_present:
        if department not in schedules:
            logger.warning(
                f"Не найдено расписание для {config.DEPARTMENT_NAMES[department]}"
            )
            if os.environ.get("APP_ENVIRONMENT") == "runtime":
                flask.flash(
                    f"Не найдено расписание для {config.DEPARTMENT_NAMES[department]}",
                    "warning",
                )




if __name__ == "__main__":
    load_schedules(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/approved",
        "2021-01-01",
    )
