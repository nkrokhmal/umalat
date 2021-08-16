from app.imports.runtime import *
from app.scheduler.mozzarella.properties import (
    cast_properties as parse_schedule_mozzarella,
)
from app.scheduler.mozzarella.parser import (
    parse_properties as parse_properties_mozzarella,
)


from app.scheduler.ricotta.properties import cast_properties as parse_schedule_ricotta
from app.scheduler.mascarpone.properties import (
    cast_properties as parse_schedule_mascarpone,
)
from app.scheduler.milk_project.properties import (
    cast_properties as parse_schedule_milk_project,
)
from app.scheduler.butter.properties import cast_properties as parse_schedule_butter
from app.scheduler.adygea.properties import cast_properties as parse_schedule_adygea

PARSERS = {
    "mozzarella": parse_schedule_mozzarella,
    "ricotta": parse_schedule_ricotta,
    "mascarpone": parse_schedule_mascarpone,
    "milk_project": parse_schedule_milk_project,
    "butter": parse_schedule_butter,
    "adygea": parse_schedule_adygea,
}


def load_properties(schedules, path=None, prefix=None):
    properties = {}

    for department in [
        "mozzarella",
        "ricotta",
        "milk_project",
        "butter",
        "mascarpone",
        "adygea",
    ]:
        if department in schedules:
            properties[department] = PARSERS[department](schedules[department])
        else:
            if department == "mozzarella" and path and prefix:
                fn = os.path.join(path, f"{prefix} Расписание моцарелла.xlsx")
                if os.path.exists(fn):
                    properties["mozzarella"] = parse_properties_mozzarella(fn)
                else:
                    properties[department] = PARSERS[department]()
            else:
                properties[department] = PARSERS[department]()
    return properties


def assert_properties_presence(
    properties, raise_if_not_present=None, warn_if_not_present=None
):
    raise_if_not_present = raise_if_not_present or []
    warn_if_not_present = warn_if_not_present or []

    for department in raise_if_not_present:
        if not properties[department].is_present():
            raise Exception(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}"
            )

    for department in warn_if_not_present:
        if not properties[department].is_present():
            logger.warning(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}"
            )
            if os.environ.get("APP_ENVIRONMENT") == "runtime":
                flask.flash(
                    f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}",
                    "warning",
                )
