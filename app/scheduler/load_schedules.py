from app.imports.runtime import *
from utils_ak.block_tree import *
import flask


def load_schedules(path, prefix):
    schedules = {}
    for department, display_name in [
        ["mozzarella", "Расписание моцарелла"],
        ["mascarpone", "Расписание маскарпоне"],
        ["butter", "Расписание масло"],
        ["milk_project", "Расписание милкпроджект"],
        ["ricotta", "Расписание рикотта"],
        ["adygea", "Расписание адыгейский"],
    ]:
        fn = os.path.join(path, prefix + " " + display_name + ".pickle")

        if not os.path.exists(fn):
            if department in config.EMPTY_DEPARTMENTS_ALLOWED:
                logger.warning(f"'{display_name}' не найдено.")
                if os.environ.get("APP_ENVIRONMENT") == "runtime":
                    flask.flash(f"'{display_name}' не найдено.", "warning")
                continue
            else:
                raise Exception(f"'{display_name}' не найдено.")

        with open(fn, "rb") as f:
            schedules[department] = ParallelepipedBlock.from_dict(pickle.load(f))

    return schedules


if __name__ == "__main__":
    load_schedules(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/approved",
        "2021-01-01",
    )
