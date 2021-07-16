from app.imports.runtime import *
from utils_ak.block_tree import *


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
            # todo maybe: make properly, use generic config, not DebugConfig
            if department in config.EMPTY_DEPARTMENTS_ALLOWED:
                pass

            if department in ["mozzarella", "ricotta", "mascarpone"]:
                raise Exception(f"Не найдено: {display_name} для данной даты")
            else:
                continue

        with open(fn, "rb") as f:
            schedules[department] = ParallelepipedBlock.from_dict(pickle.load(f))

    return schedules
