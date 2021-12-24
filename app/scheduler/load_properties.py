from app.imports.runtime import *
from app.scheduler.mozzarella.properties import (
    cast_properties as parse_schedule_mozzarella,
)
from app.scheduler.mozzarella.parser import (
    parse_properties as parse_properties_mozzarella,
)


from app.scheduler.ricotta.properties import cast_properties as parse_schedule_ricotta
from app.scheduler.ricotta.parser import parse_properties as parse_properties_ricotta

from app.scheduler.mascarpone.properties import (
    cast_properties as parse_schedule_mascarpone,
)
from app.scheduler.mascarpone.parser import (
    parse_properties as parse_properties_mascarpone,
)

from app.scheduler.milk_project.properties import (
    cast_properties as parse_schedule_milk_project,
)
from app.scheduler.milk_project.parser import (
    parse_properties as parse_properties_milk_project,
)

from app.scheduler.butter.properties import cast_properties as parse_schedule_butter
from app.scheduler.butter.parser import parse_properties as parse_properties_butter

from app.scheduler.adygea.properties import cast_properties as parse_schedule_adygea
from app.scheduler.adygea.parser import parse_properties as parse_properties_adygea

SCHEDULE_PARSERS = {
    "mozzarella": parse_schedule_mozzarella,
    "ricotta": parse_schedule_ricotta,
    "mascarpone": parse_schedule_mascarpone,
    "milk_project": parse_schedule_milk_project,
    "butter": parse_schedule_butter,
    "adygea": parse_schedule_adygea,
}

EXCEL_PARSERS = {
    "mozzarella": parse_properties_mozzarella,
    "ricotta": parse_properties_ricotta,
    "mascarpone": parse_properties_mascarpone,
    "milk_project": parse_properties_milk_project,
    "butter": parse_properties_butter,
    "adygea": parse_properties_adygea,
}


def load_properties(schedules, path=None, prefix=None):
    # NOTE: RETURN BLANK PROPERTIES IF NOT PRESENT
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
            properties[department] = SCHEDULE_PARSERS[department](schedules[department])
        else:
            if path and prefix:
                fn = os.path.join(
                    path,
                    f"{prefix} Расписание {config.DEPARTMENT_ROOT_NAMES[department]}.xlsx",
                )
                if os.path.exists(fn):
                    try:
                        properties[department] = EXCEL_PARSERS[department](fn)
                    except:
                        raise
                        raise Exception(f'Произошла ошибка во время чтения параметров расписания из файла: {os.path.basename(fn)}')
                else:
                    properties[department] = SCHEDULE_PARSERS[department]()
            else:
                properties[department] = SCHEDULE_PARSERS[department]()
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


def test_load_properties():
    print(
        load_properties(
            schedules={},
            path="/Users/marklidenberg/Downloads/Telegram Desktop/",
            prefix="2021-09-03",
        )
    )


if __name__ == "__main__":
    test_load_properties()
